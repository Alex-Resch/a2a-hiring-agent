import { useState } from 'react';
import type { CalendarPhase1Request, FreeSlot, SelectedProfile, StreamResponse } from '../../shared/models';
import { streamFetch } from '../../shared/functions.ts';
import type { ConfigData } from '../../shared/types.ts';

export function useSetSelected() {
    const [agentThreeStarted, setAgentThreeStarted] = useState(false);
    const [agentThreeFinished, setAgentThreeFinished] = useState(false);
    const [isError, setIsError] = useState(false);
    const [freeSlots, setFreeSlots] = useState<FreeSlot[]>([]);

    const onSubmit = async (selected_profiles: SelectedProfile[], data: ConfigData) => {
        const calendarPhase1Request: CalendarPhase1Request = {
            selected_profiles,
            work_start_hour: data.work_start_hour,
            work_end_hour: data.work_end_hour,
            appointment_duration: data.appointment_duration,
        };
        await streamFetch('/calendar/slots', calendarPhase1Request, (response: StreamResponse) => {
            if (response.status?.includes('Agent 3 is checking')) setAgentThreeStarted(true);
            if (response.status?.includes('Error')) setIsError(true);
            if (response.status === 'Free slots found') setAgentThreeFinished(true);

            if (response.free_slots) setFreeSlots(response.free_slots);
        });
    };

    return {
        onSubmit,
        freeSlots,
        isError,
        agentThreeStarted,
        agentThreeFinished,
        setFreeSlots,
    };
}
