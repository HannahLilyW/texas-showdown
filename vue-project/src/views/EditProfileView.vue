<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import type { Ref } from 'vue';
import router from '../router';
import ShirtIcon from '../components/icons/IconShirt.vue';
import HatIcon from '../components/icons/IconHat.vue';
import BackgroundIcon from '../components/icons/IconBackground.vue';
import SkintoneIcon from '../components/icons/IconSkintone.vue';
import {
    username, name, is_guest, background_color, shirt_color, skin_color, hat_color,
    postWithoutAuth, updateToken, updateUsername, post, get
} from '../services/api.js';

const profilePicCanvas: Ref<HTMLCanvasElement|null> = ref(null);

const activeTab: Ref<string> = ref('background');
const newName: Ref<string> = ref(name.value);

const error: Ref<boolean|string> = ref(false);

watch(newName, () => {
    invalid.value = !newName.value.length;
})

const invalid: Ref<boolean> = ref(!newName.value.length);

const backgroundActive = computed(() => ({
  'tab-active': activeTab.value === 'background'
}))

const skinActive = computed(() => ({
  'tab-active': activeTab.value === 'skin'
}))

const shirtActive = computed(() => ({
  'tab-active': activeTab.value === 'shirt'
}))

const hatActive = computed(() => ({
  'tab-active': activeTab.value === 'hat'
}))

function activateTab(tab: string) {
    activeTab.value = tab;
}

const colors = [
    'black',
    'red',
    'blue',
    'brown',
    'green',
    'yellow',
    'purple',
    'gray',
    'white',
    'skin1',
    'skin2',
    'skin3',
    'skin4',
    'blank'
]

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

function randomColor() {
    return colors[Math.floor(Math.random() * colors.length)];
}

let selections: Record<string, string> = {
    "background": background_color.value,
    'shirt': shirt_color.value,
    'skin': skin_color.value,
    'hat': hat_color.value
}

function drawBackground(ctx: CanvasRenderingContext2D) {
    if (selections['background'] != 'blank') {
        ctx.fillStyle = colorsToHex[selections['background']];
        ctx.fillRect(0, 0, 100, 100);
    }
}

function drawShirt(ctx: CanvasRenderingContext2D) {
    if (selections['shirt'] != 'blank') {
        ctx.fillStyle = colorsToHex[selections['shirt']];
        ctx.beginPath();
        ctx.arc(50, 120, 50, 0, 2 * Math.PI);
        ctx.fill();
    }
}

function drawSkin(ctx: CanvasRenderingContext2D) {
    if (selections['skin'] != 'blank') {
        ctx.fillStyle = colorsToHex[selections['skin']];
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
    ctx.fillStyle = colorsToHex[selections['hat']];
    ctx.fill(path);
    ctx.restore();
}

function updateProfilePic(color: string) {
    selections[activeTab.value] = color;
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

function postEditProfile() {
    post('players/edit_profile/', {
        'name': newName.value,
        'background_color': selections['background'],
        'shirt_color': selections['shirt'],
        'skin_color': selections['skin'],
        'hat_color': selections['hat']
    }).then(response => {
        try {
            response.json().then(responseJson => {
                if (response.status != 200) {
                    error.value = `Error updating profile: ${responseJson.toString()}`;
                    return;
                }
                name.value = responseJson['name'];
                is_guest.value = responseJson['is_guest'];
                background_color.value = responseJson['background_color'];
                shirt_color.value = responseJson['shirt_color'];
                skin_color.value = responseJson['skin_color'];
                hat_color.value = responseJson['hat_color'];
                router.push('/');
            })
        } catch (e) {
            error.value = `Error updating profile: ${e}`;
        }
    })
}

function save() {
    if (!invalid.value) {
        if (!username.value) {
            const characters = 'abcdefghijklmnopqrstuvwxyz0123456789';
            let newUsername = 'guest_';
            for (let i = 0; i < 10; i++) {
                newUsername += characters.charAt(Math.floor(Math.random() * characters.length));
            }
            let newPassword = '';
            for (let i = 0; i < 32; i++) {
                newPassword += characters.charAt(Math.floor(Math.random() * characters.length));
            }
            postWithoutAuth('create_account/', {
                'username': newUsername,
                'password': newPassword,
                'is_guest': true
            }).then(response => {
                try {
                    response.json().then(responseJson => {
                        if (response.status != 200) {
                            error.value = `Error creating account: ${responseJson.toString()}`;
                            return;
                        }
                        if (responseJson['token'] && responseJson['username']) {
                            updateToken(responseJson['token']);
                            updateUsername(responseJson['username']);
                            postEditProfile();
                        } else {
                            error.value = 'Error creating account: Bad response from server';
                        }
                    })
                } catch (e) {
                    error.value = `Error creating account: ${e}`;
                }
            })
        } else {
            postEditProfile();
        }
    }
}

onMounted(() => {
    get(`players/${username.value}/profile_info/`).then(response => {
        try {
          response.json().then(responseJson => {
            selections['background'] = responseJson['background_color'];
            selections['shirt'] = responseJson['shirt_color'];
            selections['skin'] = responseJson['skin_color'];
            selections['hat'] = responseJson['hat_color'];
            updateProfilePic(selections['background']);
          })
        } catch (e) {
          console.log(`Error getting profile info: ${e}`)
        }
    })
})

</script>

<template>
<div class="edit-profile-container">
    <input type="text" placeholder="Enter your name" v-model="newName" maxlength="32">
    <div>
        <canvas height="100" width="100" id="profilePicCanvas" ref="profilePicCanvas"></canvas>
    </div>
    <div class="tabs-row">
        <div class="tab" :class="backgroundActive" @click="activateTab('background')">
            <BackgroundIcon class="icon-small"></BackgroundIcon>
        </div>
        <div class="tab" :class="skinActive" @click="activateTab('skin')">
            <SkintoneIcon class="icon-small"></SkintoneIcon>
        </div>
        <div class="tab" :class="shirtActive" @click="activateTab('shirt')">
            <ShirtIcon class="icon-small"></ShirtIcon>
        </div>
        <div class="tab" :class="hatActive" @click="activateTab('hat')">
            <HatIcon class="icon-small"></HatIcon>
        </div>
    </div>
    <div id="colorPicker">
        <div v-for="color in colors" :key="color">
            <div class="color" :class="color" @click="updateProfilePic(color)"></div>
        </div>
    </div>
    <div class="buttons-row">
        <div class="button rye" @click="save()" :class="{disabled: invalid}">SAVE</div>
    </div>
    <div class="error" v-if="error">{{ error }}</div>
</div>
</template>

<style scoped>
.edit-profile-container {
    display: flex;
    flex-direction: column;
    align-items: center;
}

input {
    padding: 4px;
    margin: 4px;
    margin-top: 20px;
}

#colorPicker {
    background-color: var(--color-button);
    width: calc(100% - 16px);
    margin-left: 8px;
    margin-right: 8px;
    border-radius: 8px;

    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 8px;
}

.color {
    width: 40px;
    height: 40px;
    margin: 8px;
    border-radius: 8px;
    cursor: pointer;
}

.blank {
    border: 2px dashed var(--color-card-background);
}

#profilePicCanvas {
    border-radius: 8px;
}

</style>