<script setup lang="ts">

    const backendUrl = "/texas_api/";

    // Form data
    let text: string = "";
    let password: string = "";
    let retypePassword: string = "";

    function createAccount(event: Event) {

        // Needed because by default, pressing a button in a form will reload the page. We don't want that.
        event.preventDefault();

        // Send the data
        fetch(backendUrl).then(r => {
            console.log(r);
        })
    };
</script>

<template>
    <header>
        Create New Account
    </header>
    <div>
        Usernames and passwords may consist of letters, numbers, and underscores, with a maximum length of 64 characters.
    </div>
    
    <form>
        <div class="form-row">
            <label for="username">Username:</label>
            <input id="username" v-model="text" maxlength="64">
        </div>
        <div class="form-row">
            <label for="password">New Password:</label>
            <input id="password" type="password" v-model="password" maxlength="64">
        </div>
        <div class="form-row">
            <label for="retypePassword">Retype Password:</label>
            <input id="retypePassword" type="password" v-model="retypePassword" maxlength="64">
        </div>
        <button @click="createAccount($event)">Create New Account</button>
    </form>
</template>

<style scoped>
label {
    margin-right: 8px;
}
.form-row {
    margin-top: 8px;
}
</style>