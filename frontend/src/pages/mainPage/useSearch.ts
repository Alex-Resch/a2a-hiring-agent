import { useState } from 'react';
import type { SearchFormData } from '../../shared/types';
import type { ProfileScore, StreamResponse } from '../../shared/models';
import { streamFetch } from '../../shared/functions.ts';

export function useSearch() {
    const [modalOpen, setModalOpen] = useState(true);
    const [agentOneStarted, setAgentOneStarted] = useState(false);
    const [agentOneFinished, setAgentOneFinished] = useState(false);
    const [agentTwoStarted, setAgentTwoStarted] = useState(false);
    const [agentTwoFinished, setAgentTwoFinished] = useState(false);
    const [scoredProfiles, setScoredProfiles] = useState<ProfileScore[]>([]);
    const [statusText, setStatusText] = useState('');

    const onSubmit = async (data: SearchFormData) => {
        await streamFetch('/search', data, (response: StreamResponse) => {
            if (response.status) setStatusText(response.status);

            if (response.status?.includes('Agent 1 is searching')) setAgentOneStarted(true);
            if (response.status?.includes('profiles found')) setAgentOneFinished(true);
            if (response.status?.includes('Agent 2 is scoring')) setAgentTwoStarted(true);
            if (response.status?.includes('Done')) setAgentTwoFinished(true);

            if (response.scored_profiles) setScoredProfiles(response.scored_profiles);
        });
    };

    return {
        onSubmit,
        modalOpen,
        setModalOpen,
        agentOneStarted,
        agentOneFinished,
        agentTwoStarted,
        agentTwoFinished,
        scoredProfiles,
        statusText,
    };
}
