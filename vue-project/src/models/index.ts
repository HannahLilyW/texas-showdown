export type Game = {
    id: number,
    created: Date,
    created_by: string,
    num_players: number,
    betting: boolean,
    is_betting_round: boolean,
    pot: number,
    is_started: boolean,
    owner: string,
    player_set: Player[],
    turn: number,
    hand: number,
    turnhistory_set: TurnHistory[]
    is_finished: boolean,
    winners: string[]
}

export type GameMetadata = {
    id: number,
    created: Date,
    owner: string
}

export type Player = {
    username: string,
    position: number,
    is_turn: boolean,
    waiting_for_continue: boolean,
    tricks: number,
    score: number,
    money: number,
    bet: number,
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
