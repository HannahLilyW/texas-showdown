import { io } from "socket.io-client";

const socket = io();

socket.on("connect", () => {
    console.log('connected!');
});

socket.onAny((eventName, ...args) => {
    console.log('caught some event')
    console.log(eventName)
    console.log(args)
});
