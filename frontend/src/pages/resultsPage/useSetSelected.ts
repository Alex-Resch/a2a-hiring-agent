import { useState } from "react"
import type {FreeSlot, SelectedProfile} from "../../shared/models"
import {streamFetch} from "../../shared/functions.ts";

export function useSetSelected() {
    const [agentThreeStarted, setAgentThreeStarted] = useState(false)
    const [agentThreeFinished, setAgentThreeFinished] = useState(false)
    const [isError, setIsError] = useState(false)
    const [freeSlots, setFreeSlots] = useState<FreeSlot[]>([])

    const onSubmit = async (selected_profiles: SelectedProfile[]) => {
        await streamFetch("/calendar/slots", { selected_profiles }, (response: any) => {
            if (response.status.includes("Agent 3 is checking"))    setAgentThreeStarted(true)
            if (response.status.includes("Error"))                  setIsError(true)
            if (response.status === "Free slots found")                         setAgentThreeFinished(true)

            if (response.free_slots) setFreeSlots(response.free_slots)
        })
    }

    return {
        onSubmit,
        freeSlots,
        isError,
        agentThreeStarted,
        agentThreeFinished,
        setFreeSlots,
    }
}