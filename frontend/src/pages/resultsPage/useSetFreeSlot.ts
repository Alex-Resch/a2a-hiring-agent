import type { CalendarPhase2Request, FreeSlot, SelectedProfile, StreamResponse } from '../../shared/models.ts';
import { useState } from 'react';
import { streamFetch } from '../../shared/functions.ts';

export function useSetFreeSlot() {
    const [creatingAppointmentStarted, setCreatingAppointmentStarted] = useState(false);
    const [agentThreeFinished, setAgentThreeFinished] = useState(false);
    const [isError, setIsError] = useState(false);

    const onSubmit = async (selectedSlot: FreeSlot, selectedProfiles: SelectedProfile[]) => {
        const mockedProfiles: SelectedProfile[] = [
            { username: 'testuser1', email: 'alex.resch02@gmail.com' },
            { username: 'testuser2', email: 'alex.resch.dev@gmail.com' },
        ];
        selectedProfiles = mockedProfiles;

        const calendarPhase2Request: CalendarPhase2Request = {
            selected_slot: selectedSlot,
            selected_profiles: selectedProfiles,
        };

        await streamFetch('/calendar/schedule', calendarPhase2Request, (response: StreamResponse) => {
            if (response.status?.includes('Agent 3 is scheduling appointment')) setCreatingAppointmentStarted(true);
            if (response.status?.includes('Error')) setIsError(true);

            if (response.status === 'Done' || response.status === 'Error') {
                setCreatingAppointmentStarted(false);
                setAgentThreeFinished(true);
            }
        });
    };

    return {
        onSubmit,
        creatingAppointmentStarted,
        agentThreeIsDone: agentThreeFinished,
        isError,
    };
}
