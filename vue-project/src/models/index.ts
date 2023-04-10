export type Game = {
    id: number,
    created: Date,
    created_by: string,
    num_players: number,
    betting: boolean,
    is_started: boolean,
    owner: string,
    player_set: Player[],
    turn: number,
    hand: number,
    turnhistory_set: TurnHistory[]
}

export type Player = {
    username: string,
    position: number,
    is_turn: boolean,
    waiting_for_continue: boolean,
    tricks: number,
    score: number
}

export type TurnHistory = {
    turn: number,
    hand: number,
    player: string,
    card: number
}
