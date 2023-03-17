import { io, Socket } from "socket.io-client";

let socket: Socket|null = null;

export function start() {
    if (socket) {
        socket.close();
    }
    socket = io();

    socket.on("connect", () => {
        console.log('connected!');
    });

    socket.on("disconnect", () => {
        console.log('disconnected!');
    })
    
    socket.onAny((eventName, ...args) => {
        console.log('caught some event')
        console.log(eventName)
        console.log(args)
    });
}

export function stop() {
    if (socket) {
        socket.close();
    }
}
