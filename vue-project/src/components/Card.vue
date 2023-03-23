<script setup lang="ts">
import PistolIcon from './icons/IconPistol.vue';
import BootIcon from './icons/IconBoot.vue';
import HatIcon from './icons/IconHat.vue';
import HorseshoeIcon from './icons/IconHorseshoe.vue';
import CactusIcon from './icons/IconCactus.vue';
import StarIcon from './icons/IconStar.vue';
import WheelIcon from './icons/IconWheel.vue';
import SkullIcon from './icons/IconSkull.vue';
import { computed } from 'vue'

const props = defineProps(['number'])

const color = computed(() => {
    for (let key in colorsToNumbers) {
        if (colorsToNumbers[key].indexOf(Number(props.number)) != -1) {
            return key;
        }
    }
    return 'black';
})

const colorsToNumbers: Record<string, number[]> = {
    "black": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "red": [11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
    "blue": [21, 22, 23, 24, 25, 26, 27, 28, 29],
    "brown": [31, 32, 33, 34, 35, 36, 37, 38],
    "green": [41, 42, 43, 44, 45, 46, 47],
    "yellow": [51, 52, 53, 54, 55, 56],
    "purple": [61, 62, 63, 64, 65],
    "gray": [71, 72, 73, 74]
}

const colorsToHex: Record<string, string> = {
    "black": "#010206",
    "red": "#F2653E",
    "blue": "#1F85B8",
    "brown": "#905532",
    "green": "#2DAC5E",
    "yellow": "#F8A940",
    "purple": "#8B489C",
    "gray": "#818688",
}

</script>

<template>
<div class="card">
    <div class="column-1">
        <div class="meter" :class="{empty: number > props.number}" v-for="number in colorsToNumbers[color]"></div>
        <div class="meter-head" :class="{filled: Number(props.number) == colorsToNumbers[color].slice(-1)[0]}">{{ colorsToNumbers[color].length }}</div>
    </div>
    <div class="column-2">
        <div class="number">{{ props.number }}</div>
        <div class="icon">
            <PistolIcon v-if="color == 'black'"></PistolIcon>
            <BootIcon v-if="color == 'red'"></BootIcon>
            <HatIcon v-if="color == 'blue'"></HatIcon>
            <HorseshoeIcon v-if="color == 'brown'"></HorseshoeIcon>
            <CactusIcon v-if="color == 'green'"></CactusIcon>
            <StarIcon v-if="color == 'yellow'"></StarIcon>
            <WheelIcon v-if="color == 'purple'"></WheelIcon>
            <SkullIcon v-if="color == 'gray'"></SkullIcon>
        </div>
    </div>
</div>
</template>

<style>

.column-1 {
    display: flex;
    flex-direction: column-reverse;
    justify-content: space-between;
    gap: 2px;
    align-items: center;
    font-size: 12px;
}

.meter-head {
    color: v-bind(colorsToHex[color]);
    border: 2px solid v-bind(colorsToHex[color]);
    height: 24px;
    width: 24px;
    text-align: center;
    border-radius: 50%;
}

.filled {
    background-color: v-bind(colorsToHex[color]);
    color: var(--color-card-background);
}

.meter {
    background-color: v-bind(colorsToHex[color]);
    width: 8px;
    height: 100%;
}

.empty {
    background-color: #BBBBBB;
}

.card {
    background-color: var(--color-card-background);
    height: 90px;
    width: 70px;
    border-radius: 4px;
    border: 4px solid var(--color-card-background);
    display: flex;
    justify-content: space-between;
}

.number {
    color: v-bind(colorsToHex[color]);
}

.column-2 {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
}

path {
    color: v-bind(colorsToHex[color]);
}
</style>