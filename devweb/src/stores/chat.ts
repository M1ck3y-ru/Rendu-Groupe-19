import { defineStore } from 'pinia';
import { ref } from 'vue';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export const useChatStore = defineStore('chat', () => {
  // Default to empty string to use Vite local proxy (bypasses CORS issue)
  const serverUrl = ref('');
  const isConnected = ref(false);
  const availableModels = ref<string[]>([]);
  const selectedModel = ref('Phi-3.5-Financial');
  
  // Inference parameters
  const temperature = ref(0.7);
  const topP = ref(0.9);
  const maxTokens = ref(512);

  // Chat state
  const messages = ref<Message[]>([]);
  const isGenerating = ref(false);
  const isChecking = ref(false);
  const lastChecked = ref('');
  const latency = ref<number | null>(null);

  // Connection check (GET to /ollama-status if using proxy, or root of absolute URL)
  const checkConnection = async () => {
    if (isChecking.value) return;
    isChecking.value = true;
    const startTime = performance.now();

    try {
      const baseUrl = serverUrl.value ? serverUrl.value.replace(/\/$/, '') : '';
      const checkUrl = baseUrl ? `${baseUrl}/` : '/ollama-status';

      const response = await fetch(checkUrl, {
        method: 'GET',
        headers: {
          'Accept': 'application/json, text/plain, */*',
          'ngrok-skip-browser-warning': 'true'
        },
        signal: AbortSignal.timeout(3500)
      });

      if (response.ok) {
        isConnected.value = true;
        latency.value = Math.round(performance.now() - startTime);
        
        // Also fetch models list to update available models
        await fetchModels();
      } else {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      isConnected.value = false;
      latency.value = null;
      availableModels.value = [];
    } finally {
      isChecking.value = false;
      const now = new Date();
      lastChecked.value = now.toLocaleTimeString();
    }
  };

  // Discovered models from /api/tags
  const fetchModels = async () => {
    try {
      const baseUrl = serverUrl.value ? serverUrl.value.replace(/\/$/, '') : '';
      const response = await fetch(`${baseUrl}/api/tags`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'ngrok-skip-browser-warning': 'true'
        },
        signal: AbortSignal.timeout(3500)
      });

      if (response.ok) {
        const data = await response.json();
        const modelNames = data.models?.map((m: any) => m.name) || [];
        availableModels.value = modelNames;
      }
    } catch (error) {
      console.error('Failed to fetch models:', error);
    }
  };

  // Reset inference parameters
  const resetParams = () => {
    temperature.value = 0.7;
    topP.value = 0.9;
    maxTokens.value = 512;
  };

  // Send message and stream reply from Ollama
  const sendMessage = async (userText: string, onUpdate: () => void) => {
    if (!userText.trim() || isGenerating.value) return;
    if (!isConnected.value) {
      throw new Error("Le serveur Ollama est actuellement déconnecté.");
    }

    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // 1. Add User Message
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: userText,
      timestamp: timeStr
    };
    messages.value.push(userMsg);
    onUpdate();

    // 2. Add Assistant Shell Message
    const assistantId = crypto.randomUUID();
    const assistantMsg: Message = {
      id: assistantId,
      role: 'assistant',
      content: '',
      timestamp: timeStr
    };
    messages.value.push(assistantMsg);
    isGenerating.value = true;
    onUpdate();

    try {
      const baseUrl = serverUrl.value ? serverUrl.value.replace(/\/$/, '') : '';
      const fetchUrl = `${baseUrl}/api/chat`;

      // Translate user-facing selectedModel to Ollama registered model name.
      // "Phi-3.5-Financial" -> "phi3-financial:latest"
      let modelToUse = selectedModel.value;
      if (modelToUse === 'Phi-3.5-Financial') {
        if (availableModels.value.includes('phi3-financial:latest')) {
          modelToUse = 'phi3-financial:latest';
        } else if (availableModels.value.includes('phi3.5:latest')) {
          modelToUse = 'phi3.5:latest';
        }
      }

      // Convert history format to Ollama's API schema (excluding current empty assistant message)
      const apiHistory = messages.value.slice(0, -1).map(m => ({
        role: m.role,
        content: m.content
      }));

      const response = await fetch(fetchUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify({
          model: modelToUse,
          messages: apiHistory,
          stream: true,
          options: {
            temperature: temperature.value,
            top_p: topP.value,
            num_predict: maxTokens.value
          }
        })
      });

      if (!response.ok) {
        throw new Error(`Erreur HTTP : ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder('utf-8');
      if (!reader) {
        throw new Error("Impossible de lire le flux de réponse du serveur.");
      }

      let buffer = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const parsed = JSON.parse(line);
            if (parsed.message?.content) {
              const idx = messages.value.findIndex(m => m.id === assistantId);
              if (idx !== -1) {
                messages.value[idx].content += parsed.message.content;
                onUpdate();
              }
            }
          } catch (err) {
            console.warn('Erreur parsing stream line:', line, err);
          }
        }
      }

      // Process remaining buffer
      if (buffer.trim()) {
        try {
          const parsed = JSON.parse(buffer);
          if (parsed.message?.content) {
            const idx = messages.value.findIndex(m => m.id === assistantId);
            if (idx !== -1) {
              messages.value[idx].content += parsed.message.content;
              onUpdate();
            }
          }
        } catch (err) {
          console.warn('Erreur parsing remaining buffer:', buffer, err);
        }
      }

    } catch (error: any) {
      const idx = messages.value.findIndex(m => m.id === assistantId);
      if (idx !== -1) {
        messages.value[idx].content = `❌ Erreur : Impossible de joindre le modèle. Veuillez vérifier votre connexion et l'état du serveur.\nDétails: ${error.message || error}`;
        onUpdate();
      }
    } finally {
      isGenerating.value = false;
      onUpdate();
    }
  };

  const clearHistory = () => {
    messages.value = [];
  };

  return {
    serverUrl,
    isConnected,
    availableModels,
    selectedModel,
    temperature,
    topP,
    maxTokens,
    messages,
    isGenerating,
    isChecking,
    lastChecked,
    latency,
    checkConnection,
    fetchModels,
    resetParams,
    sendMessage,
    clearHistory
  };
});
