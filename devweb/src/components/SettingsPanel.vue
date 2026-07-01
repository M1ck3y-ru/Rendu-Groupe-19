<script setup lang="ts">
import { ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useChatStore } from '../stores/chat';

const store = useChatStore();
const { serverUrl, selectedModel, availableModels, temperature, topP, maxTokens } = storeToRefs(store);

const showAdvanced = ref(false);
</script>

<template>
  <div class="settings-panel glass-panel">
    <div class="panel-section">
      <h3 class="section-title">Configuration</h3>
      
      <!-- Server URL setting -->
      <div class="input-group">
        <label for="server-url">Serveur Ollama</label>
        <input 
          id="server-url" 
          type="text" 
          v-model="serverUrl" 
          placeholder="[Proxy actif] (laissez vide)"
        />
        <span class="input-tip">Laissez vide pour utiliser le proxy Vite (contourne CORS)</span>
      </div>
      
      <!-- Model setting -->
      <div class="input-group">
        <label for="model-select">Modèle Actif</label>
        <div class="select-wrapper">
          <select 
            id="model-select" 
            v-model="selectedModel"
          >
            <option value="Phi-3.5-Financial">
              Phi-3.5-Financial (Recommandé)
            </option>
            <option 
              v-for="model in availableModels.filter(m => m !== 'phi3-financial:latest' && m !== 'Phi-3.5-Financial')" 
              :key="model" 
              :value="model"
            >
              {{ model }}
            </option>
          </select>
        </div>
        <span v-if="availableModels.length === 0" class="input-warning">
          Vérification de la connexion pour charger la liste des modèles...
        </span>
      </div>
    </div>

    <!-- Collapsible Advanced Settings -->
    <div class="panel-section border-top">
      <button class="advanced-toggle" @click="showAdvanced = !showAdvanced">
        <span>Paramètres d'inférence</span>
        <svg 
          :class="{ 'expanded': showAdvanced }" 
          width="16" 
          height="16" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          stroke-width="2" 
          stroke-linecap="round" 
          stroke-linejoin="round"
        >
          <path d="m6 9 6 6 6-6"/>
        </svg>
      </button>

      <div v-show="showAdvanced" class="advanced-content animate-fade-in">
        <!-- Temperature -->
        <div class="slider-group">
          <div class="slider-header">
            <label for="temperature">Température</label>
            <span class="slider-value">{{ temperature.toFixed(1) }}</span>
          </div>
          <input 
            id="temperature" 
            type="range" 
            min="0.1" 
            max="1.5" 
            step="0.1" 
            v-model.number="temperature"
          />
          <div class="slider-labels">
            <span>Précis</span>
            <span>Créatif</span>
          </div>
        </div>

        <!-- Top P -->
        <div class="slider-group">
          <div class="slider-header">
            <label for="top-p">Top P</label>
            <span class="slider-value">{{ topP.toFixed(2) }}</span>
          </div>
          <input 
            id="top-p" 
            type="range" 
            min="0.1" 
            max="1.0" 
            step="0.05" 
            v-model.number="topP"
          />
        </div>

        <!-- Max Tokens -->
        <div class="slider-group">
          <div class="slider-header">
            <label for="max-tokens">Max Tokens</label>
            <span class="slider-value">{{ maxTokens }}</span>
          </div>
          <input 
            id="max-tokens" 
            type="range" 
            min="128" 
            max="2048" 
            step="64" 
            v-model.number="maxTokens"
          />
        </div>
        
        <button class="reset-btn" @click="store.resetParams">
          Réinitialiser par défaut
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings-panel {
  padding: 16px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background: rgba(18, 24, 36, 0.4);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.panel-section {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.border-top {
  border-top: 1px solid var(--border-color);
  padding-top: 14px;
}

.section-title {
  margin: 0;
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-secondary);
}

input[type="text"], select {
  width: 100%;
  padding: 10px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.85rem;
  transition: all 0.2s ease;
}

.select-wrapper {
  position: relative;
}

.select-wrapper::after {
  content: "▼";
  font-size: 0.7rem;
  color: var(--text-muted);
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
}

select {
  appearance: none;
  -webkit-appearance: none;
  cursor: pointer;
  padding-right: 30px;
}

.input-tip {
  font-size: 0.7rem;
  color: var(--text-muted);
}

.input-warning {
  font-size: 0.7rem;
  color: var(--accent-emerald);
  line-height: 1.3;
}

.advanced-toggle {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-secondary);
  padding: 4px 0;
}

.advanced-toggle:hover {
  color: var(--text-primary);
}

.advanced-toggle svg {
  transition: transform 0.2s ease;
}

.advanced-toggle svg.expanded {
  transform: rotate(180deg);
}

.advanced-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 10px;
}

.slider-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.slider-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.slider-value {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--accent-emerald);
  font-family: var(--font-mono);
}

input[type="range"] {
  width: 100%;
  height: 4px;
  background: var(--bg-tertiary);
  border-radius: 9999px;
  outline: none;
  appearance: none;
  -webkit-appearance: none;
  border: none;
  padding: 0;
}

input[type="range"]::-webkit-slider-thumb {
  appearance: none;
  -webkit-appearance: none;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--accent-emerald);
  cursor: pointer;
  box-shadow: 0 0 4px var(--accent-emerald-glow);
  transition: transform 0.1s ease;
}

input[type="range"]::-webkit-slider-thumb:hover {
  transform: scale(1.2);
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.65rem;
  color: var(--text-muted);
}

.reset-btn {
  width: 100%;
  padding: 8px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.02);
}

.reset-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
  border-color: var(--text-secondary);
}
</style>
