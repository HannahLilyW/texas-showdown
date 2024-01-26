<script setup lang="ts">
import { ref, onMounted } from 'vue';
import type { Ref } from 'vue';

const props = defineProps(['background_color', 'shirt_color', 'skin_color', 'hat_color'])

const profilePicCanvas: Ref<HTMLCanvasElement|null> = ref(null);

const colorsToHex: Record<string, string> = {
    "black": "#010206",
    "red": "#F2653E",
    "blue": "#1F85B8",
    "brown": "#905532",
    "green": "#2DAC5E",
    "yellow": "#F8A940",
    "purple": "#8B489C",
    "gray": "#818688",
    "white": "#E5DFDA",
    "skin1": "#321b0f",
    "skin2": "#be9167",
    "skin3": "#ffcd94",
    "skin4": "#ffcab6",
    "blank": "#00000000"
}

function drawBackground(ctx: CanvasRenderingContext2D) {
    if (props.background_color != 'blank') {
        ctx.fillStyle = colorsToHex[props.background_color];
        ctx.fillRect(0, 0, 100, 100);
    }
}

function drawShirt(ctx: CanvasRenderingContext2D) {
    if (props.shirt_color != 'blank') {
        ctx.fillStyle = colorsToHex[props.shirt_color];
        ctx.beginPath();
        ctx.arc(50, 120, 50, 0, 2 * Math.PI);
        ctx.fill();
    }
}

function drawSkin(ctx: CanvasRenderingContext2D) {
    if (props.skin_color != 'blank') {
        ctx.fillStyle = colorsToHex[props.skin_color];
        ctx.beginPath();
        ctx.arc(50, 50, 25, 0, 2 * Math.PI);
        ctx.fill();
    }
}

function drawHat(ctx: CanvasRenderingContext2D) {
    ctx.save();
    ctx.scale(70/32,70/32);
    ctx.translate(15,-6);
    ctx.rotate(0.4);
    const path = new Path2D('M17.389 3.209c-0.036 0.005-0.142 0.023-0.241 0.038-0.604 0.094-1.205 0.34-2.423 0.992-0.327 0.175-0.766 0.403-0.977 0.508-0.208 0.104-0.563 0.307-0.787 0.454-0.853 0.556-1.124 0.647-2.423 0.807-1.19 0.15-1.507 0.233-2.157 0.576-0.5 0.264-0.98 0.601-1.766 1.243-0.228 0.185-0.596 0.475-0.815 0.64-0.926 0.7-1.261 1.081-1.452 1.642-0.266 0.794-0.292 1.748-0.076 2.893 0.071 0.383 0.272 1.172 0.439 1.738 0.239 0.807 0.388 1.345 0.492 1.746l0.101 0.386-0.221 0.117c-0.698 0.376-1.045 0.591-1.512 0.944-0.586 0.447-1.649 1.629-2.238 2.497-1.119 1.642-1.485 3.121-1.16 4.674 0.292 1.391 1.023 2.357 2.231 2.946 0.553 0.269 1.299 0.492 2.119 0.632 1.254 0.216 1.987 0.152 4.2-0.368 1.127-0.264 1.183-0.279 1.764-0.454 0.272-0.081 0.736-0.218 1.028-0.305 2.165-0.634 4.162-1.421 5.484-2.157 1.852-1.030 3.53-2.299 6.202-4.679 0.231-0.206 0.619-0.53 0.863-0.721 0.934-0.728 1.809-1.467 2.728-2.302 0.294-0.266 0.711-0.622 0.926-0.787 2.205-1.693 2.997-2.525 3.9-4.098 0.624-1.086 0.873-1.723 0.914-2.337 0.025-0.398-0.084-0.769-0.307-1.035-0.051-0.061-0.091-0.134-0.091-0.162 0-0.117 0.005-0.117-0.726-0.16-0.34-0.020-0.657 0.041-1.317 0.256-0.614 0.2-0.802 0.307-1.16 0.645-0.14 0.132-0.434 0.452-0.652 0.711-0.607 0.716-0.891 0.962-1.297 1.132-0.355 0.15-0.667 0.203-1.434 0.241-0.579 0.028-0.908 0.061-1.205 0.117-0.226 0.043-0.167 0.099-0.505-0.472-0.33-0.553-0.561-1.020-0.957-1.941-0.338-0.787-0.736-1.609-1.348-2.791-0.601-1.155-0.906-1.647-1.388-2.246-0.233-0.292-0.84-0.901-1.084-1.089-0.239-0.188-0.571-0.365-0.784-0.424-0.134-0.036-0.759-0.069-0.888-0.046z');
    ctx.fillStyle = colorsToHex[props.hat_color];
    ctx.fill(path);
    ctx.restore();
}

function drawProfilePic() {
    if (profilePicCanvas.value) {
        let ctx: CanvasRenderingContext2D | null = profilePicCanvas.value.getContext('2d');
        if (ctx) {
            ctx.fillStyle = "rgba(255, 255, 255, 0.0)";
            ctx.clearRect(0, 0, 100, 100);
            drawBackground(ctx);
            drawShirt(ctx);
            drawSkin(ctx);
            drawHat(ctx);
        }
    }
}

onMounted(() => {
    drawProfilePic();
})

</script>

<template>
<canvas height="100" width="100" id="profilePicCanvas" ref="profilePicCanvas"></canvas>
</template>

<style>
#profilePicCanvas {
    border-radius: 8px;
}
</style>