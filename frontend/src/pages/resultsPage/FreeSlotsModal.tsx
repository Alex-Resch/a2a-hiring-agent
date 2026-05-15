import {useEffect, useState} from "react"
import type {FreeSlot, SelectedProfile} from "../../shared/models"
import {useSetFreeSlot} from "./useSetFreeSlot.ts";
import {X} from "lucide-react";

type FreeSlotsModalProps = {
    freeSlots: FreeSlot[];
    selectedProfiles: SelectedProfile[];
    onDone: () => void;
    onClose: () => void;
}

export default function FreeSlotsModal({ freeSlots, selectedProfiles, onDone, onClose }: FreeSlotsModalProps) {
    const [selectedSlot, setSelectedSlot] = useState<FreeSlot>()
    const { onSubmit, creatingAppointmentStarted, agentThreeIsDone, isError } = useSetFreeSlot()

    useEffect(() => {
        if (agentThreeIsDone) {
            onDone()
        }
    }, [agentThreeIsDone])

    const formatSlot = (slot: FreeSlot) => {
        const start = new Date(slot.start)
        const end = new Date(slot.end)
        return {
            date: start.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" }),
            time: `${start.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" })} – ${end.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" })}`,
        }
    }

    const handleSetSelect = async (e: React.FormEvent) => {
        e.preventDefault()

        if (!selectedSlot) return
        await onSubmit(selectedSlot, selectedProfiles)
    }

    return (
        <dialog className="modal modal-open">
            <div className="modal-box max-w-lg">
                <div className="flex items-start justify-between mb-1">
                    <h3 className="font-bold text-lg">Select Interview Slot</h3>
                    <button className="btn btn-sm btn-circle btn-ghost" type="button" onClick={onClose}>
                        <X size={16} />
                    </button>
                </div>
                <p className="text-xs text-base-content/50 mb-5">Choose a time that works for the interview</p>

                <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
                    {freeSlots.map((slot, i) => {
                        const { date, time } = formatSlot(slot)
                        const isSelected = selectedSlot === slot
                        return (
                            <div
                                key={i}
                                onClick={() => setSelectedSlot(slot)}
                                className={`flex items-center justify-between p-3 rounded-box border cursor-pointer transition-all
                                    ${isSelected ? "border-primary bg-primary/5" : "border-base-300 hover:border-primary/50"}`}
                            >
                                <div>
                                    <p className="text-sm font-medium">{date}</p>
                                    <p className="text-xs text-base-content/50">{time}</p>
                                </div>
                            </div>
                        )
                    })}
                </div>

                <div className="modal-action mt-5">
                    {creatingAppointmentStarted && !isError && (
                        <div className="flex items-center gap-2 text-xs text-base-content/50">
                            <span className="loading loading-spinner loading-xs text-primary" />
                            Agent 3 is scheduling the appointment...
                        </div>
                    )}
                    {isError && (
                        <div className="alert alert-error text-xs py-2">
                            Something went wrong while creating the appointment.
                        </div>
                    )}
                    <button
                        className="btn btn-primary btn-sm"
                        disabled={!selectedSlot}
                        type="button"
                        onClick={handleSetSelect}
                    >
                        Confirm Slot
                    </button>
                </div>
            </div>
            <div className="modal-backdrop" onClick={onClose} />
        </dialog>
    )
}