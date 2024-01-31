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
    owner_name: string,
    player_set: Player[],
    turn: number,
    hand: number,
    turnhistory_set: TurnHistory[]
    betturnhistory_set: BetTurnHistory[]
    is_finished: boolean,
    winners: string[],
    last_timer_reset: Date
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
    waiting_for_continue: boolean,
    tricks: number,
    score: number,
    money: number,
    bet: number,
    fold: boolean
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

export type BetTurnHistory = {
    bet_turn: number,
    hand: number,
    player: string,
    bet_action: string,
    bet_amount: number,
    player_money: number
}
