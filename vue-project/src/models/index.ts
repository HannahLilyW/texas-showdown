export type Game = {
    id: number,
    created: Date,
    created_by: string,
    num_players: number,
    pot: number,
    is_started: boolean,
    owner: string,
    owner_name: string,
    player_set: Player[],
    turn: number,
    hand: number,
    buy_in: number,
    turnhistory_set: TurnHistory[],
    is_finished: boolean,
    winners: PlayerName[],
    last_timer_reset: Date,
    is_private: boolean
}

export type PlayerName = {
    username: string,
    name: string
}

export type GameMetadata = {
    id: number,
    created: Date,
    owner: string
}

export type Player = {
    username: string,
    name?: string,
    background_color?: string,
    shirt_color?: string,
    skin_color?: string,
    hat_color?: string,
    position: number,
    is_turn: boolean,
    choose_turn: boolean,
    waiting_for_continue: boolean,
    tricks: number,
    score: number,
    money: number
}

export type PlayerStatistic = {
    username: string,
    wins: number,
    losses: number
}

export type TurnHistory = {
    turn: number,
    hand: number,
    player: string,
    card: number|null,
    end_game: boolean
}

export type Chat = {
    username: string,
    chat: string
}