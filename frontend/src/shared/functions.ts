const BASE_URL = "http://localhost:8000"

export async function streamFetch(url: string, data: unknown, onEvent: (parsed: any) => void) {
    const response = await fetch(BASE_URL + url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    })

    const reader = response.body!.getReader()
    const decoder = new TextDecoder()

    while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const text = decoder.decode(value)
        const lines = text.split("\n").filter(line => line.startsWith("data: "))

        for (const line of lines) {
            const parsed = JSON.parse(line.replace("data: ", ""))
            onEvent(parsed)

            if (parsed.status === "Done" || parsed.status === "Error") {
                reader.cancel()
                return
            }
        }
    }
}