export type SearchFormData = {
    languages: string[];
    frameworks: string[];
    domains: string[];
    locations: string[];
    experience_levels: string[];
    availability: string[];
    min_years_experience: number;
    active_within_months: number;
    min_public_repos: number;
    min_stars: number;
};

export type ConfigData = {
    work_start_hour: number;
    work_end_hour: number;
    appointment_duration: number;
};
