import { create } from 'zustand';

// Ultimate features - always enabled
export interface VersionFeatures {
    hasPdfExport: boolean;
    hasWebUI: boolean;
    hasAuth: boolean;
    hasOpenEnded: boolean;
    hasAIFeedback: boolean;
}

interface AppState {
    getFeatures: () => VersionFeatures;
}

// App is now locked to Ultimate (v0.4) features
const ultimateFeatures: VersionFeatures = {
    hasPdfExport: true,
    hasWebUI: true,
    hasAuth: true,
    hasOpenEnded: true,
    hasAIFeedback: true,
};

export const useAppStore = create<AppState>()(() => ({
    getFeatures: () => ultimateFeatures,
}));
