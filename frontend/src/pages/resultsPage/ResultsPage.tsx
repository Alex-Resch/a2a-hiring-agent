import { useLocation, useNavigate } from 'react-router-dom';
import { TrendingUp, TrendingDown, Code2, Activity, Layers, Users, ArrowLeft, X } from 'lucide-react';
import type { ProfileScore, SelectedProfile } from '../../shared/models';
import { useState } from 'react';
import PageHeader from '../../shared/components/PageHeader';
import { useSetSelected } from './useSetSelected.ts';
import FreeSlotsModal from './FreeSlotsModal.tsx';

const SCORE_CATEGORIES = [
    {
        key: 'code_quality_score',
        label: 'Code Quality',
        icon: <Code2 size={12} />,
        color: 'text-primary',
    },
    {
        key: 'activity_score',
        label: 'Activity',
        icon: <Activity size={12} />,
        color: 'text-secondary',
    },
    {
        key: 'technical_breadth_score',
        label: 'Tech Breadth',
        icon: <Layers size={12} />,
        color: 'text-accent',
    },
    {
        key: 'community_impact_score',
        label: 'Community Impact',
        icon: <Users size={12} />,
        color: 'text-info',
    },
] as const;

function ScoreRing({ score }: { score: number }) {
    const color = score >= 75 ? 'text-success' : score >= 50 ? 'text-warning' : 'text-error';
    return (
        <div
            className={`radial-progress ${color} font-bold text-sm`}
            style={
                {
                    '--value': score,
                    '--size': '3.5rem',
                    '--thickness': '4px',
                } as React.CSSProperties
            }
            aria-label={`Score: ${score}`}
        >
            {score}
        </div>
    );
}

function CandidateCard({ profile, rank, selected, onToggle }: { profile: ProfileScore; rank: number; selected: boolean; onToggle: () => void }) {
    const [expanded, setExpanded] = useState(false);
    const rankColors = ['badge-primary', 'badge-secondary', 'badge-accent'];

    return (
        <div className={`card bg-base-100 border shadow-sm transition-all ${selected ? 'border-primary' : 'border-base-300'}`}>
            <div className="card-body gap-4 p-5">
                {/* Header */}
                <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                        <ScoreRing score={Math.round(profile.overall_score)} />
                        <span className={`badge ${rankColors[rank]} badge-sm font-bold`}>#{rank + 1}</span>
                        <h4 className="font-semibold text-lg">{profile.name}</h4>
                    </div>
                    <input type="checkbox" className="checkbox checkbox-primary checkbox-sm" checked={selected} onChange={onToggle} />
                </div>

                {/* Sub-scores */}
                <div className="grid grid-cols-2 gap-2">
                    {SCORE_CATEGORIES.map(({ key, label, icon, color }) => (
                        <div key={key} className="flex items-center gap-2 text-xs">
                            <span className="font-mono font-medium w-8">{profile[key]}/25</span>
                            <span className={`flex items-center gap-1 ${color}`}>
                                {icon} {label}
                            </span>
                        </div>
                    ))}
                </div>

                {/* Collapsible Strengths & Weaknesses */}
                <div className="collapse collapse-arrow border border-base-300 rounded-box">
                    <input type="checkbox" checked={expanded} onChange={() => setExpanded((p) => !p)} />
                    <div className="collapse-title text-xs font-semibold py-2 min-h-0">Strengths & Weaknesses</div>
                    <div className="collapse-content">
                        <div className="grid grid-cols-2 gap-3 text-xs pt-1">
                            <div>
                                <p className="flex items-center gap-1 font-semibold text-success mb-1">
                                    <TrendingUp size={12} /> Strengths
                                </p>
                                <ul className="space-y-0.5 text-base-content/70">
                                    {profile.strengths.map((s, i) => (
                                        <li key={i}>· {s}</li>
                                    ))}
                                </ul>
                            </div>
                            <div>
                                <p className="flex items-center gap-1 font-semibold text-error mb-1">
                                    <TrendingDown size={12} /> Weaknesses
                                </p>
                                <ul className="space-y-0.5 text-base-content/70">
                                    {profile.weaknesses.map((w, i) => (
                                        <li key={i}>· {w}</li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                        <p className="text-xs font-semibold text-base-content/70 mt-3 mb-1">Agent 2 Reasoning:</p>
                        <p className="text-xs text-base-content/50 leading-relaxed">{profile.reasoning}</p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default function ResultsPage() {
    const { state } = useLocation();
    const navigate = useNavigate();
    const scoredProfiles: ProfileScore[] = state?.scoredProfiles ?? [];
    const sorted = [...scoredProfiles].sort((a, b) => b.overall_score - a.overall_score);
    const [selected, setSelected] = useState<SelectedProfile[]>([]);
    const [showSlotModal, setShowSlotModal] = useState(true);
    const [appointmentDone, setAppointmentDone] = useState(false);

    const { onSubmit, freeSlots, isError, agentThreeStarted, agentThreeFinished } = useSetSelected();

    const toggleSelect = (username: string, email: string | null) => {
        const isSelected = selected.some((p) => p.username === username);

        if (!isSelected) {
            setSelected((prev) => [...prev, { username, email }]);
        } else {
            setSelected((prev) => prev.filter((p) => p.username !== username));
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setShowSlotModal(true);
        await onSubmit(selected);
    };

    return (
        <form onSubmit={handleSubmit}>
            <div className="min-h-screen bg-base-200 py-10 px-4 md:px-10">
                <div className="max-w-3xl mx-auto space-y-6">
                    {/* Header */}
                    <PageHeader
                        title="Top Candidates"
                        subtitle={`${sorted.length} candidates ranked by Agent 2`}
                        action={
                            <button className="btn btn-ghost btn-sm gap-1" onClick={() => navigate('/')}>
                                <ArrowLeft size={14} /> New Search
                            </button>
                        }
                    />

                    {appointmentDone && (
                        <div className="alert alert-success flex items-center justify-between">
                            <span>🎉 Appointment scheduled! Invitations have been sent to all selected candidates.</span>
                            <div className="flex items-center gap-2">
                                <button className="btn btn-sm btn-ghost" onClick={() => navigate('/')}>
                                    <ArrowLeft size={14} /> Back to Home
                                </button>
                                <button className="btn btn-sm btn-circle btn-ghost" onClick={() => setAppointmentDone(false)}>
                                    <X size={14} />
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Candidate Cards */}
                    {sorted.length === 0 ? (
                        <div className="card bg-base-100 border border-base-300">
                            <div className="card-body items-center text-center py-12">
                                <p className="text-base-content/40 text-sm">No candidates found.</p>
                                <button className="btn btn-primary btn-sm mt-3" onClick={() => navigate('/')}>
                                    Back to Search
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {sorted.map((profile, i) => (
                                <CandidateCard
                                    key={profile.name}
                                    profile={profile}
                                    rank={i}
                                    selected={selected.some((p) => p.username === profile.name)}
                                    onToggle={() => toggleSelect(profile.name, profile.email)}
                                />
                            ))}
                        </div>
                    )}

                    <div className="flex items-center justify-between bg-base-100 border border-base-300 rounded-box p-4">
                        <p className="text-sm text-base-content/70">
                            {selected.length} candidate
                            {selected.length > 1 ? 's' : ''} selected
                        </p>
                        <button type="submit" className="btn btn-primary btn-sm" disabled={selected.length === 0}>
                            {agentThreeStarted && !agentThreeFinished && <span className="loading loading-spinner loading-xs" />}
                            Proceed with selected
                        </button>
                    </div>

                    {agentThreeStarted && !agentThreeFinished && freeSlots.length === 0 && !isError && (
                        <div className="flex items-center gap-2 text-xs text-base-content/50">
                            <span className="loading loading-dots loading-xs text-primary" />
                            Agent 3 is checking your calendar for free slots...
                        </div>
                    )}

                    {agentThreeFinished && freeSlots.length === 0 && !isError && (
                        <div className="alert alert-warning text-sm">⚠️ Agent 3 has finished but found no free slots in the next 7 days.</div>
                    )}

                    {isError && (
                        <div className="alert alert-error text-sm">❌ Something went wrong while checking the calendar. Please try again.</div>
                    )}
                </div>
            </div>

            {showSlotModal && freeSlots.length > 0 && (
                <FreeSlotsModal
                    freeSlots={freeSlots}
                    selectedProfiles={selected}
                    onDone={() => {
                        setShowSlotModal(false);
                        setAppointmentDone(true);
                    }}
                    onClose={() => setShowSlotModal(false)}
                />
            )}
        </form>
    );
}
