import { BarChart2, Bot, ChevronRight, LucideCoffee, Search, X } from 'lucide-react';
import type { ProfileScore } from '../../shared/models';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

type AgentProgressModalProps = {
    modalOpen: boolean;
    setModalOpen: (open: boolean) => void;
    agentOneStarted: boolean;
    agentOneFinished: boolean;
    agentTwoStarted: boolean;
    agentTwoFinished: boolean;
    scoredProfiles: ProfileScore[];
    statusText: string;
};

export default function AgentProgressModal({
    modalOpen,
    setModalOpen,
    agentOneStarted,
    agentOneFinished,
    agentTwoStarted,
    agentTwoFinished,
    scoredProfiles,
    statusText,
}: AgentProgressModalProps) {
    const navigate = useNavigate();

    useEffect(() => {
        if (agentTwoFinished) {
            navigate('/results', { state: { scoredProfiles } });
        }
    }, [agentTwoFinished, scoredProfiles, navigate]);

    return (
        <dialog className={`modal ${modalOpen ? 'modal-open' : ''}`}>
            <div className="modal-box max-w-lg">
                {/* Modal Header */}
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h3 className="font-bold text-lg">Searching for Candidates</h3>
                        <p className="text-xs text-base-content/50 mt-0.5">
                            Agents are working <LucideCoffee size={12} className="inline-block" />
                        </p>
                    </div>
                    {agentTwoFinished && (
                        <button className="btn btn-ghost btn-sm btn-circle" onClick={() => setModalOpen(false)}>
                            <X size={16} />
                        </button>
                    )}
                </div>

                {/* Steps */}
                <ul className="steps steps-horizontal w-full text-xs mb-6">
                    <li className="step step-primary">
                        <span className="flex items-center gap-1">
                            <Bot size={12} /> Criteria set
                        </span>
                    </li>
                    <li className={`step ${agentOneStarted ? 'step-primary' : ''}`}>
                        <span className="flex items-center gap-1">
                            {agentOneStarted && !agentOneFinished ? <span className="loading loading-spinner loading-xs" /> : <Search size={12} />}
                            Agent 1
                        </span>
                    </li>
                    <li className={`step ${agentTwoStarted ? 'step-primary' : ''}`}>
                        <span className="flex items-center gap-1">
                            {agentTwoStarted && !agentTwoFinished ? <span className="loading loading-spinner loading-xs" /> : <BarChart2 size={12} />}
                            Agent 2
                        </span>
                    </li>
                    <li className={`step ${agentTwoFinished ? 'step-primary' : ''}`}>
                        <span className="flex items-center gap-1">
                            <ChevronRight size={12} /> Review Top 3
                        </span>
                    </li>
                </ul>

                {/* Live Status Text */}
                {statusText && (
                    <div className="flex items-center gap-2 text-xs text-base-content/50 mb-6">
                        {!agentTwoFinished && <span className="loading loading-dots loading-xs text-primary" />}
                        <span>{statusText}</span>
                    </div>
                )}
            </div>

            {/* Click outside to close only when done */}
            {agentTwoFinished && <div className="modal-backdrop" onClick={() => setModalOpen(false)} />}
        </dialog>
    );
}
