import { ref } from 'vue';
import type { Ref } from 'vue';

export const music: Ref<HTMLAudioElement> = ref(new Audio("/sounds/oldwesternmusic.mp3"));
