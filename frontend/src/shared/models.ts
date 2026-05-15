export interface ProfileScore {
    name: string;
    email: string | null;
    overall_score: number;
    code_quality_score: number;
    activity_score: number;
    technical_breadth_score: number;
    community_impact_score: number;
    strengths: string[]
    weaknesses: string[]
    reasoning: string
}

export interface FreeSlot {
    start: Date
    end: Date
}

export interface SelectedProfile {
    username: string;
    email: string | null;
}

export interface CalendarPhase2Request {
    selected_profiles: SelectedProfile[]
    selected_slot: FreeSlot
}
