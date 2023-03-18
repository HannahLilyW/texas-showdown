export type Game = {
    id: number,
    created: Date,
    created_by: string,
    num_players: number,
    betting: boolean,
    is_started: boolean,
    owner: string,
    player_set: string[]
}