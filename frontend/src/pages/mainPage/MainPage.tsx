import { useState } from "react"
import {useForm, type UseFormRegister} from "react-hook-form"
import {
    Search, Code2, Boxes, Globe, BarChart2, CalendarClock,
    GitFork, Star, Briefcase, Clock, Bot, ChevronRight, SlidersHorizontal,
} from "lucide-react"
import AgentProgressModal from "./AgentProgessModal"
import { useSearch } from "./useSearch"
import PageHeader from "../../shared/components/PageHeader.tsx";


const LANGUAGES = [
    "Python", "TypeScript", "JavaScript", "Go", "Rust",
    "Java", "C#", "C++", "Ruby", "Swift", "PHP", "Kotlin",
]
const FRAMEWORKS = [
    "React", "Next.js", "Vue", "FastAPI", "Django",
    "Spring Boot", "Node.js", "LangChain", "PydanticAI",
    "PyTorch", "TensorFlow", "Flutter",
]
const DOMAINS = [
    "AI / ML", "Web Dev", "DevOps / Cloud", "Mobile",
    "Embedded", "Data Engineering", "Security", "Blockchain",
]
const LOCATIONS = [
    "Germany", "Austria", "Switzerland", "Netherlands",
    "USA", "UK", "France", "Canada", "India", "Remote",
]
const EXPERIENCE_LEVELS = ["Junior", "Mid-level", "Senior", "Lead / Principal"]
const AVAILABILITY = ["Full-time", "Part-time", "Freelance"]

const ICON_SM = 15
const ICON_XS = 14
const CLS_SECTION_HEADER = "text-sm font-semibold flex items-center gap-2 mb-3 text-base-content/70"
const tabCls = (active: boolean) =>
    `tab gap-1.5 font-medium text-sm ${active ? "tab-active" : "text-base-content/50"}`

const TABS = [
    { label: "Tech Stack", icon: <Code2 size={ICON_SM} /> },
    { label: "Domain & Location", icon: <Globe size={ICON_SM} /> },
    { label: "Experience", icon: <Briefcase size={ICON_SM} /> },
    { label: "Filters", icon: <SlidersHorizontal size={ICON_SM} /> },
]

type SearchFormData = {
    languages: string[]
    frameworks: string[]
    domains: string[]
    locations: string[]
    experience_levels: string[]
    availability: string[]
    min_years_experience: number
    active_within_months: number
    min_public_repos: number
    min_stars: number
}

function CheckboxChips({
    options,
    fieldName,
    register,
}: {
    options: string[]
    fieldName: keyof SearchFormData
    register: UseFormRegister<SearchFormData>
}) {
    return (
        <div className="flex flex-wrap gap-2">
            {options.map((opt) => (
                <label key={opt} className="cursor-pointer select-none">
                    <input
                        type="checkbox"
                        value={opt}
                        {...register(fieldName)}
                        className="sr-only peer"
                    />
                    <span className="badge badge-outline text-sm py-3 px-3 transition-all duration-150 peer-checked:badge-primary peer-checked:border-primary">
                        {opt}
                    </span>
                </label>
            ))}
        </div>
    )
}

export default function SearchPage() {
    const [activeTab, setActiveTab] = useState(0)

    const {
        onSubmit, modalOpen, setModalOpen,
        agentOneStarted, agentOneFinished,
        agentTwoStarted, agentTwoFinished,
        scoredProfiles, statusText,
    } = useSearch()

    const { register, handleSubmit, watch } = useForm<SearchFormData>({
        defaultValues: {
            languages: [], frameworks: [], domains: [], locations: [],
            experience_levels: [], availability: [],
            min_years_experience: 0, active_within_months: 12,
            min_public_repos: 0, min_stars: 0,
        },
    })

    const minYears = watch("min_years_experience")
    const activeMonths = watch("active_within_months")

    return (
        <div className="min-h-screen bg-base-200 py-10 px-4 md:px-10">
            <div className="max-w-4xl mx-auto space-y-6">

                <PageHeader
                    title="Find Developer Talent"
                    subtitle="Define your criteria. Two AI agents will scan GitHub and return the best-matched profiles ranked by fit."
                />

                {/* Agent Pipeline Steps */}
                <div className="card bg-base-100 border border-base-300 shadow-sm">
                    <div className="card-body py-4 px-6">
                        <ul className="steps steps-horizontal w-full text-xs">
                            <li className="step step-primary step-no-line">
                                <span className="flex items-center gap-1"><Bot size={12} /> Set Criteria</span>
                            </li>
                            <li className="step step-primary step-no-line">
                                <span className="flex items-center gap-1"><Search size={12} /> Agent 1 searches GitHub</span>
                            </li>
                            <li className="step step-primary step-no-line">
                                <span className="flex items-center gap-1"><BarChart2 size={12} /> Agent 2 screens &amp; ranks</span>
                            </li>
                            <li className="step step-primary step-no-line">
                                <span className="flex items-center gap-1"><ChevronRight size={12} /> You review Top 3</span>
                            </li>
                        </ul>
                    </div>
                </div>

                {/* Main Form */}
                <form onSubmit={handleSubmit(onSubmit)}>
                    <div className="card bg-base-100 border border-base-300 shadow-sm">
                        <div className="card-body gap-5">

                            {/* Tabs */}
                            <div role="tablist" className="tabs tabs-bordered">
                                {TABS.map((tab, i) => (
                                    <button
                                        key={tab.label}
                                        type="button"
                                        role="tab"
                                        onClick={() => setActiveTab(i)}
                                        className={tabCls(activeTab === i)}
                                    >
                                        {tab.icon}
                                        {tab.label}
                                    </button>
                                ))}
                            </div>

                            {/* Tab 0 – Tech Stack */}
                            {activeTab === 0 && (
                                <div className="space-y-6">
                                    <div>
                                        <h2 className={CLS_SECTION_HEADER}>
                                            <Code2 size={ICON_SM} className="text-primary" />
                                            Programming Languages
                                        </h2>
                                        <CheckboxChips options={LANGUAGES} fieldName="languages" register={register} />
                                    </div>
                                    <div className="divider my-0" />
                                    <div>
                                        <h2 className={CLS_SECTION_HEADER}>
                                            <Boxes size={ICON_SM} className="text-secondary" />
                                            Frameworks &amp; Libraries
                                        </h2>
                                        <CheckboxChips options={FRAMEWORKS} fieldName="frameworks" register={register} />
                                    </div>
                                </div>
                            )}

                            {/* Tab 1 – Domain & Location */}
                            {activeTab === 1 && (
                                <div className="space-y-6">
                                    <div>
                                        <h2 className={CLS_SECTION_HEADER}>
                                            <Boxes size={ICON_SM} className="text-accent" />
                                            Domain / Specialization
                                        </h2>
                                        <CheckboxChips options={DOMAINS} fieldName="domains" register={register} />
                                    </div>
                                    <div className="divider my-0" />
                                    <div>
                                        <h2 className={CLS_SECTION_HEADER}>
                                            <Globe size={ICON_SM} className="text-info" />
                                            Location
                                        </h2>
                                        <CheckboxChips options={LOCATIONS} fieldName="locations" register={register} />
                                    </div>
                                </div>
                            )}

                            {/* Tab 2 – Experience */}
                            {activeTab === 2 && (
                                <div className="space-y-6">
                                    <div>
                                        <h2 className={CLS_SECTION_HEADER}>
                                            <BarChart2 size={ICON_SM} className="text-warning" />
                                            Experience Level
                                        </h2>
                                        <CheckboxChips options={EXPERIENCE_LEVELS} fieldName="experience_levels" register={register} />
                                    </div>
                                    <div className="divider my-0" />
                                    <div>
                                        <h2 className={CLS_SECTION_HEADER}>
                                            <Clock size={ICON_SM} className="text-success" />
                                            Availability
                                        </h2>
                                        <CheckboxChips options={AVAILABILITY} fieldName="availability" register={register} />
                                    </div>
                                </div>
                            )}

                            {/* Tab 3 – Filters */}
                            {activeTab === 3 && (
                                <div className="space-y-6">
                                    <div>
                                        <div className="flex justify-between mb-2">
                                            <label className="text-sm font-medium flex items-center gap-1.5">
                                                <BarChart2 size={ICON_XS} className="text-primary" />
                                                Min. Years of Experience
                                            </label>
                                            <span className="text-sm font-mono text-primary tabular-nums">
                                                {minYears} {minYears === 1 ? "yr" : "yrs"}
                                            </span>
                                        </div>
                                        <input
                                            type="range" min="0" max="15" step="1"
                                            className="range range-primary range-sm w-full"
                                            {...register("min_years_experience", { valueAsNumber: true })}
                                        />
                                        <div className="flex justify-between text-xs text-base-content/30 mt-1 px-0.5">
                                            <span>0</span><span>5</span><span>10</span><span>15+</span>
                                        </div>
                                    </div>

                                    <div>
                                        <div className="flex justify-between mb-2">
                                            <label className="text-sm font-medium flex items-center gap-1.5">
                                                <CalendarClock size={ICON_XS} className="text-secondary" />
                                                Active Within
                                            </label>
                                            <span className="text-sm font-mono text-secondary tabular-nums">
                                                {activeMonths} months
                                            </span>
                                        </div>
                                        <input
                                            type="range" min="1" max="24" step="1"
                                            className="range range-secondary range-sm w-full"
                                            {...register("active_within_months", { valueAsNumber: true })}
                                        />
                                        <div className="flex justify-between text-xs text-base-content/30 mt-1 px-0.5">
                                            <span>1m</span><span>6m</span><span>12m</span><span>24m</span>
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <label className="text-sm font-medium flex items-center gap-1.5 mb-2">
                                                <GitFork size={ICON_XS} className="text-accent" />
                                                Min. Public Repos
                                            </label>
                                            <input
                                                type="number" min="0" placeholder="e.g. 5"
                                                className="input input-bordered input-sm w-full"
                                                {...register("min_public_repos", { valueAsNumber: true })}
                                            />
                                        </div>
                                        <div>
                                            <label className="text-sm font-medium flex items-center gap-1.5 mb-2">
                                                <Star size={ICON_XS} className="text-warning" />
                                                Min. Repo Stars
                                            </label>
                                            <input
                                                type="number" min="0" placeholder="e.g. 10"
                                                className="input input-bordered input-sm w-full"
                                                {...register("min_stars", { valueAsNumber: true })}
                                            />
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Submit Bar */}
                    <div className="mt-4 flex justify-end">
                        <button type="submit" className="btn btn-primary gap-2">
                            <Search size={16} />
                            Search Candidates
                        </button>
                    </div>
                </form>

            </div>

            <AgentProgressModal
                modalOpen={modalOpen}
                setModalOpen={setModalOpen}
                agentOneStarted={agentOneStarted}
                agentOneFinished={agentOneFinished}
                agentTwoStarted={agentTwoStarted}
                agentTwoFinished={agentTwoFinished}
                scoredProfiles={scoredProfiles}
                statusText={statusText}
            />
        </div>
    )
}