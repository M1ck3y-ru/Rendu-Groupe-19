<script setup lang="ts">
import { ref, nextTick } from 'vue';
import { storeToRefs } from 'pinia';
import { useChatStore } from '../stores/chat';

const store = useChatStore();
const { messages, isGenerating, isConnected, selectedModel, serverUrl } = storeToRefs(store);

const inputMessage = ref('');
const scrollContainer = ref<HTMLDivElement | null>(null);

// Suggestions
const suggestions = [
  "Quelles sont les méthodes d'évaluation d'une entreprise fintech ?",
  "Explique le fonctionnement du ratio d'endettement d'une société.",
  "Analyse les implications de l'augmentation des taux directeurs sur le marché obligataire.",
  "Rédige une note d'analyse sur l'impact de l'IA générative dans l'automatisation comptable."
];

// Helper to scroll to bottom
const scrollToBottom = async () => {
  await nextTick();
  if (scrollContainer.value) {
    scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight;
  }
};

// Formatting text (bold, lists, inline code, code blocks)
const formatContent = (text: string) => {
  if (!text) return '';
  
  // Escape HTML to prevent XSS
  let escaped = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
    
  // Handle code blocks: ```code```
  escaped = escaped.replace(/```([\s\S]*?)```/g, (_, code) => {
    return `<pre class="code-block"><code>${code.trim()}</code></pre>`;
  });
  
  // Handle inline code: `code`
  escaped = escaped.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');
  
  // Handle bold text: **text**
  escaped = escaped.replace(/\*\*([\s\S]*?)\*\*/g, '<strong>$1</strong>');

  // Handle list items
  escaped = escaped.replace(/^\s*[-*]\s+(.+)/gm, '• $1');
  
  // Handle new lines
  escaped = escaped.replace(/\n/g, '<br>');
  
  return escaped;
};

const selectSuggestion = (suggestion: string) => {
  inputMessage.value = suggestion;
};

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isGenerating.value) return;
  if (!isConnected.value) {
    alert("Impossible d'envoyer le message : le serveur Ollama est déconnecté.");
    return;
  }

  const userText = inputMessage.value;
  inputMessage.value = '';

  try {
    await store.sendMessage(userText, scrollToBottom);
  } catch (err: any) {
    alert(err.message || "Erreur de communication avec le serveur.");
  }
};

const handleClearHistory = () => {
  if (confirm("Voulez-vous vraiment effacer l'historique des conversations ?")) {
    store.clearHistory();
  }
};
</script>

<template>
  <div class="chat-container">
    <!-- Header -->
    <header class="chat-header glass-panel">
      <div class="header-info">
        <div class="model-badge">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
            <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
            <line x1="12" y1="22.08" x2="12" y2="12" />
          </svg>
          <span class="model-name">{{ selectedModel || 'Phi-3.5-Financial (Non spécifié)' }}</span>
        </div>
        <span class="header-title">TechCorp Financial Assistant</span>
      </div>
      
      <button 
        v-if="messages.length > 0" 
        class="clear-btn" 
        @click="handleClearHistory" 
        title="Effacer la conversation"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 6h18" />
          <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
          <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
        </svg>
        <span>Effacer</span>
      </button>
    </header>

    <!-- Chat Area -->
    <div class="chat-messages" ref="scrollContainer">
      <!-- Empty Welcome View -->
      <div v-if="messages.length === 0" class="welcome-container animate-fade-in">
        <div class="welcome-icon">
          <span>📊</span>
        </div>
        <h2>Assistant Financier TechCorp</h2>
        <p>
          Bienvenue sur l'interface sécurisée de gestion financière et d'analyse. Posez vos questions relatives au trading, bilans de performance, régulations ou ratios financiers.
        </p>
        
        <div class="suggestions-grid">
          <div 
            v-for="s in suggestions" 
            :key="s" 
            class="suggestion-card glass-panel"
            @click="selectSuggestion(s)"
          >
            <span>{{ s }}</span>
            <span class="card-arrow">→</span>
          </div>
        </div>
      </div>

      <!-- Messages View -->
      <div v-else class="messages-list">
        <div 
          v-for="msg in messages" 
          :key="msg.id" 
          class="message-wrapper"
          :class="msg.role"
        >
          <!-- Avatar -->
          <div class="message-avatar">
            <span v-if="msg.role === 'user'">👤</span>
            <span v-else>🤖</span>
          </div>

          <!-- Bubble -->
          <div class="message-bubble glass-panel">
            <div class="bubble-meta">
              <span class="sender-name">{{ msg.role === 'user' ? 'Vous' : 'TechCorp AI' }}</span>
              <span class="message-time">{{ msg.timestamp }}</span>
            </div>
            
            <div 
              class="bubble-content" 
              v-html="formatContent(msg.content)"
            ></div>
            
            <!-- Dynamic cursor if generating -->
            <div v-if="msg.role === 'assistant' && msg.content === '' && isGenerating" class="typing-loader">
              <span class="dot"></span>
              <span class="dot"></span>
              <span class="dot"></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Bar -->
    <footer class="chat-input-bar glass-panel">
      <form @submit.prevent="sendMessage" class="input-form">
        <textarea 
          v-model="inputMessage" 
          @keydown.enter.prevent="sendMessage"
          placeholder="Posez une question financière au modèle Phi-3.5-Financial..."
          rows="1"
          class="chat-input"
          :disabled="isGenerating || !isConnected"
        ></textarea>
        
        <button 
          type="submit" 
          class="send-btn" 
          :disabled="!inputMessage.trim() || isGenerating || !isConnected"
          title="Envoyer le message"
        >
          <svg v-if="!isGenerating" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
          <div v-else class="spinning-loader"></div>
        </button>
      </form>
      <div class="input-footer-tip">
        Mode d'inférence directe sécurisé • Connecté à {{ serverUrl }}
      </div>
    </footer>
  </div>
</template>

<style>
/* Global formats for parsed HTML (cannot be scoped due to v-html) */
.bubble-content {
  font-size: 0.95rem;
  line-height: 1.6;
  word-break: break-word;
}

.bubble-content p {
  margin-bottom: 8px;
}

.bubble-content p:last-child {
  margin-bottom: 0;
}

.inline-code {
  font-family: var(--font-mono);
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.85rem;
  color: var(--accent-emerald);
}

.code-block {
  font-family: var(--font-mono);
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-color);
  padding: 12px;
  border-radius: 8px;
  font-size: 0.85rem;
  overflow-x: auto;
  margin: 10px 0;
  white-space: pre-wrap;
  color: #e2e8f0;
}

.code-block code {
  background: transparent;
  padding: 0;
  color: inherit;
}
</style>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: var(--bg-primary);
  overflow: hidden;
}

/* Header */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 24px;
  border-radius: 0;
  border-bottom: 1px solid var(--border-color);
  background: rgba(10, 14, 23, 0.6);
  z-index: 10;
}

.header-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.model-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 2px 8px;
  background: rgba(14, 165, 233, 0.1);
  border: 1px solid rgba(14, 165, 233, 0.2);
  border-radius: 9999px;
  color: var(--accent-blue);
  font-family: var(--font-mono);
  font-size: 0.75rem;
  font-weight: 600;
  width: fit-content;
}

.header-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-primary);
}

.clear-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.clear-btn:hover {
  background: rgba(239, 68, 68, 0.08);
  border-color: rgba(239, 68, 68, 0.3);
  color: var(--accent-danger);
}

/* Chat Messages */
.chat-messages {
  flex-grow: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
}

/* Welcome Container */
.welcome-container {
  max-width: 680px;
  margin: auto;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 40px 20px;
}

.welcome-icon {
  font-size: 3rem;
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(16, 185, 129, 0.1);
  border: 2px dashed rgba(16, 185, 129, 0.3);
  border-radius: 24px;
  margin-bottom: 8px;
}

.welcome-container h2 {
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(135deg, var(--text-primary) 30%, var(--accent-emerald) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.welcome-container p {
  color: var(--text-secondary);
  font-size: 0.95rem;
  line-height: 1.6;
  margin-bottom: 12px;
}

.suggestions-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  width: 100%;
  margin-top: 16px;
}

@media (max-width: 600px) {
  .suggestions-grid {
    grid-template-columns: 1fr;
  }
}

.suggestion-card {
  padding: 16px;
  text-align: left;
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  background: rgba(18, 24, 36, 0.3);
}

.suggestion-card:hover {
  background: rgba(16, 185, 129, 0.05);
  border-color: rgba(16, 185, 129, 0.3);
  color: var(--text-primary);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.card-arrow {
  color: var(--accent-emerald);
  font-weight: 700;
  opacity: 0;
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.suggestion-card:hover .card-arrow {
  opacity: 1;
  transform: translateX(4px);
}

/* Messages List */
.messages-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
}

.message-wrapper {
  display: flex;
  gap: 16px;
  width: 100%;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  flex-shrink: 0;
  margin-top: 4px;
}

.message-wrapper.assistant .message-avatar {
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.2);
}

.message-bubble {
  flex-grow: 1;
  padding: 16px 20px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: calc(100% - 52px);
}

.message-wrapper.user {
  flex-direction: row-reverse;
}

.message-wrapper.user .message-bubble {
  background: rgba(30, 41, 59, 0.5);
  border-color: rgba(255, 255, 255, 0.1);
}

.bubble-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  padding-bottom: 4px;
}

.sender-name {
  color: var(--text-secondary);
}

.message-wrapper.assistant .sender-name {
  color: var(--accent-emerald);
}

.message-time {
  color: var(--text-muted);
}

/* Typing indicator */
.typing-loader {
  display: flex;
  gap: 4px;
  padding: 8px 0;
  align-items: center;
}

.typing-loader .dot {
  width: 6px;
  height: 6px;
  background-color: var(--accent-emerald);
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-loader .dot:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-loader .dot:nth-child(3) {
  animation-delay: 0.4s;
}

/* Chat Input Bar */
.chat-input-bar {
  padding: 16px 24px;
  border-radius: 0;
  border-top: 1px solid var(--border-color);
  background: rgba(10, 14, 23, 0.8);
  max-width: 800px;
  width: calc(100% - 48px);
  margin: 0 auto 24px auto;
  border-radius: 16px;
  box-shadow: var(--shadow-lg);
}

.input-form {
  display: flex;
  gap: 12px;
  align-items: center;
}

.chat-input {
  flex-grow: 1;
  resize: none;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 12px 16px;
  color: var(--text-primary);
  font-size: 0.9rem;
  line-height: 1.4;
  height: 48px;
  max-height: 120px;
  transition: all 0.2s ease;
}

.chat-input:focus {
  border-color: var(--accent-emerald);
  box-shadow: 0 0 8px var(--accent-emerald-glow);
  background: rgba(0, 0, 0, 0.3);
}

.chat-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: var(--accent-emerald);
  color: var(--bg-primary);
  flex-shrink: 0;
  box-shadow: 0 4px 10px rgba(16, 185, 129, 0.2);
}

.send-btn:hover:not(:disabled) {
  background: var(--accent-emerald-hover);
  transform: translateY(-1px);
  box-shadow: 0 6px 14px rgba(16, 185, 129, 0.3);
}

.send-btn:disabled {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  box-shadow: none;
  cursor: not-allowed;
}

.spinning-loader {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-top-color: var(--text-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.input-footer-tip {
  font-size: 0.7rem;
  color: var(--text-muted);
  text-align: center;
  margin-top: 8px;
}
</style>
