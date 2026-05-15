type PageHeaderProps = {
    title: string
    subtitle: string
    action?: React.ReactNode
}

export default function PageHeader({ title, subtitle, action }: PageHeaderProps) {
    return (
        <div className="flex items-start justify-between flex-wrap gap-4">
            <div>
                <div className="flex items-center gap-2 mb-1">
                    <span className="badge badge-primary badge-sm font-semibold uppercase tracking-widest">
                        A2A Recruiting
                    </span>
                </div>
                <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
                <p className="text-base-content/50 text-sm mt-1">{subtitle}</p>
            </div>
            {action}
        </div>
    )
}