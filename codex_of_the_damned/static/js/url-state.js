class UrlState {
    constructor(callback, multi) {
        this.state = {}
        this.callback = callback
        this.multi = new Set(multi || [])
        window.addEventListener("popstate", async (ev) => await this.setup())
    }
    async setup() {
        this.base_location = window.location.href.split("?", 1)[0]
        if (window.location.search) {
            const params = new URLSearchParams(window.location.search)
            for (let elem of document.getElementsByClassName("translation-link")) {
                elem.href = elem.href.split("?")[0] + "?" + params.toString()
            }
            this.state = {}
            for (const [k, v] of params) {
                if (this.multi.has(k)) {
                    this.state[k] = v.split("|")
                } else {
                    this.state[k] = v
                }
            }
        } else {
            this.state = {}
        }
        await this.callback(this.state)
    }
    update(obj) {
        this.state = { ...this.state, ...obj }
        this.refresh()
    }
    remove(key) {
        if (key in this.state) {
            delete this.state[key]
            this.refresh()
        }
    }
    reset(obj = undefined) {
        this.state = obj || {}
        this.refresh()
    }
    refresh(push = true) {
        let params = ""
        if (Object.keys(this.state).length > 0) {
            params = {}
            for (const [k, v] of Object.entries(this.state)) {
                if (this.multi.has(k)) {
                    params[k] = v.join("|")
                } else {
                    params[k] = v
                }
            }
            params = "?" + new URLSearchParams(params).toString()
        }
        window.history.pushState(this.state, "", this.base_location + params)
        for (let elem of document.getElementsByClassName("translation-link")) {
            elem.href = elem.href.split("?")[0] + params
        }
    }
}
