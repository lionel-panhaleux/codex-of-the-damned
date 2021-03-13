class Completion {
    constructor(input, complete_function, message_output) {
        this.input = input
        this.complete_function = complete_function
        this.message_output = message_output
        this.choices = undefined
        this.input.addEventListener("input", async (e) => await this.complete(e))
        this.input.addEventListener("keydown", (e) => this.key(e))
        document.addEventListener("click", () => this.clear())
    }
    async complete() {
        this.clear()
        if (!this.input.value || this.input.value.length < 3) {
            return
        }
        this.focus = undefined
        this.choices = document.createElement("div")
        this.choices.classList.add("autocomplete-items")
        this.input.parentNode.appendChild(this.choices)
        try {
            this.display(await this.complete_function(this.input.value))
        } catch (error) {
            if (this.message) {
                this.message.textContent = error.message
            }
        }
    }
    key(e) {
        // arrow DOWN
        if (e.keyCode === 40) {
            if (!this.focus) {
                this.focus = this.choices.firstChild
            } else {
                this.focus.classList.remove("autocomplete-active")
                this.focus = this.focus.nextSibling
            }
            if (this.focus) {
                this.focus.classList.add("autocomplete-active")
            }
            // arrow UP
        } else if (e.keyCode === 38) {
            if (this.focus) {
                this.focus.classList.remove("autocomplete-active")
                this.focus = this.focus.previousSibling
            }
            if (this.focus) {
                this.focus.classList.add("autocomplete-active")
            }
            // ENTER
        } else if (e.keyCode === 13) {
            e.preventDefault()
            if (this.focus) {
                this.focus.click()
            }
        }
    }
    display(completion_list) {
        if (!completion_list) {
            return
        }
        for (const candidate of completion_list) {
            let b = document.createElement("div")
            b.classList.add("autocomplete-item")
            b.textContent = candidate
            b.addEventListener("click", (e) => this.choose(e))
            this.choices.appendChild(b)
        }
    }
    clear() {
        this.focus = undefined
        if (!this.choices) {
            return
        }
        this.input.parentNode.removeChild(this.choices)
        this.choices = undefined
    }
    reset() {
        this.clear()
        this.input.parentNode.reset()
    }
    choose(e) {
        this.clear()
        this.input.value = e.target.textContent
        this.input.form.dispatchEvent(
            new Event("submit", {
                bubbles: true,
                cancelable: true,
            })
        )
    }
}

async function completeCardName(text) {
    const response = await fetch(encodeURI(`https://api.krcg.org/complete/${encodeUrlParam(text)}`), {
        method: "GET",
        headers: {
            Accept: "application/json",
            "Accept-Language": document.documentElement.lang,
        },
    })
    if (!response.ok) {
        throw Error(response.statusText)
    }
    return await response.json()
}

function encodeUrlParam(param) {
    if (!param) {
        return param
    }
    // / and \ are notoriously hard to pass as parameters in the URL path
    // see https://github.com/pallets/flask/issues/900
    // just replacing them with spaces seems like the cleanest course of action
    // return encodeURIComponent(param.replace("/", " ").replace("\\", " "))
    return param.replace("/", " ").replace("\\", " ")
}
