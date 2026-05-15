import { useForm } from 'react-hook-form';
import { X } from 'lucide-react';
import type { ConfigData } from '../../shared/types.ts';

type ConfigModalProps = {
    onConfirm: (data: ConfigData) => void;
    onClose: () => void;
};

export default function ConfigModal({ onConfirm, onClose }: ConfigModalProps) {
    const { handleSubmit, register } = useForm<ConfigData>({
        defaultValues: {
            work_start_hour: 9,
            work_end_hour: 17,
            appointment_duration: 60,
        },
    });

    return (
        <dialog className="modal modal-open">
            <div className="modal-box max-w-sm">
                <div className="flex items-start justify-between mb-4">
                    <h3 className="font-bold text-lg">Interview Settings</h3>
                    <button className="btn btn-sm btn-circle btn-ghost" type="button" onClick={onClose}>
                        <X size={16} />
                    </button>
                </div>

                <div className="space-y-4">
                    <div>
                        <label className="text-sm font-medium mb-1 block">Work Start Hour</label>
                        <input
                            type="number"
                            min={0}
                            max={23}
                            className="input input-bordered input-sm w-full"
                            {...register('work_start_hour', { valueAsNumber: true })}
                        />
                    </div>
                    <div>
                        <label className="text-sm font-medium mb-1 block">Work End Hour</label>
                        <input
                            type="number"
                            min={0}
                            max={23}
                            className="input input-bordered input-sm w-full"
                            {...register('work_end_hour', { valueAsNumber: true })}
                        />
                    </div>
                    <div>
                        <label className="text-sm font-medium mb-1 block">Appointment Duration (minutes)</label>
                        <input
                            type="number"
                            min={15}
                            step={15}
                            className="input input-bordered input-sm w-full"
                            {...register('appointment_duration', { valueAsNumber: true })}
                        />
                    </div>
                    <div className="modal-action mt-2">
                        <button type="button" className="btn btn-primary btn-sm" onClick={handleSubmit(onConfirm)}>
                            Continue
                        </button>
                    </div>
                </div>
            </div>
            <div className="modal-backdrop" onClick={onClose} />
        </dialog>
    );
}
