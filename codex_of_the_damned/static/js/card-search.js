const group_map = {
    "1": " ❶",
    "2": " ❷",
    "3": " ❸",
    "4": " ❹",
    "5": " ❺",
    "6": " ❻",
    "7": " ❼",
    "ANY": "",
}
class CardSearch {
    constructor() {
        this.form = document.getElementById("card-search-form")
        this.result_message = document.getElementById("result-message")
        this.results = document.getElementById("results")
        this.card_image = document.getElementById("card-image")
        this.image_footer = document.getElementById("image-footer")
        this.card_sets = document.getElementById("card-sets")
        this.card_title = document.getElementById("card-title")
        this.card_text = document.getElementById("card-text")
        this.rulings = document.getElementById("rulings")
        this.expansions = fetchExpansions()
        this.completion = new Completion(document.getElementById("card-name"), completeCardName, this.result_message)
        this.state = new UrlState(async (data) => this.displayCard(data))
        this.form.addEventListener("submit", async (ev) => await this.submit(ev))
    }
    async submit(ev) {
        ev.preventDefault()
        const card = ev.target.elements["card-name"].value
        this.state.reset({ card: card })
        await this.displayCard(this.state.state)
        ev.target.elements["card-name"].value = ""
    }
    async selectSet(node, set_name, set_image) {
        if (this.state.set != set_name) {
            this.state.update({ set: set_name })
        }
        this.card_image.src = set_image
        this.card_image.classList.add("selectable")
        for (let item of this.card_sets.children) {
            item.classList.remove("selected")
        }
        node.classList.add("selected")
    }
    resetSet(image_url) {
        this.state.remove("set")
        this.card_image.src = image_url
        this.card_image.classList.remove("selectable")
        for (let item of this.card_sets.children) {
            item.classList.remove("selected")
        }
    }
    clear() {
        this.results.style.display = "none"
        this.card_image.src = ""
        this.image_footer.innerHTML = ""
        this.card_sets.innerHTML = ""
        this.card_title.textContent = ""
        this.card_text.innerHTML = ""
        this.result_message.innerHTML = ""
        // remove rulings, keep title
        for (const elem of this.rulings.children) {
            if (elem != this.rulings.firstElementChild) {
                this.rulings.removeChild(elem)
            }
        }
    }
    async displayCard(state) {
        this.clear()
        if (!state.card) {
            return
        }
        let data
        try {
            data = await this.fetchCard(state.card)
        } catch (error) {
            // textContent: error.message can contain the raw ?card= URL parameter
            this.result_message.textContent = error.message
        }
        if (!data) {
            return
        }
        const expansions = await this.expansions
        const lang = document.documentElement.lang
        let title = data.printed_name
        let text = data.text
        let translation
        let base_image = data.url
        const i18n = data.i18n && data.i18n[lang]
        if (i18n) {
            if (i18n.name) {
                title = i18n.name + `<br><span class="translation">${title}</span>`
            }
            if (i18n.text) {
                translation = text
                text = i18n.text
            }
            if (i18n.url && (await urlExists(i18n.url))) {
                base_image = i18n.url
            }
        }
        this.card_image.src = base_image
        this.card_image.addEventListener("click", (ev) => this.resetSet(base_image))
        if (data.group) {
            title += group_map[data.group.replace(/^G/, "").toUpperCase()] ?? ""
        }
        if (data.advanced) {
            title += " <i>|</i>"
        }
        this.card_title.innerHTML = title
        // KRCG v5: one print per set, set metadata (name, dates, bundles) comes from expansions.json
        const sets = data.prints.map((print) => {
            const expansion = expansions[print.set.code] || { name: print.set.code, release_date: null, bundles: {} }
            return {
                code: print.set.code,
                name: expansion.name,
                scan: print.url,
                prints: print.occurrences.map((occurrence) => {
                    const bundle = expansion.bundles[occurrence.bundle]
                    return {
                        ...occurrence,
                        bundle_name: bundle ? bundle.name : occurrence.bundle,
                        release_date: occurrence.date || (bundle && bundle.release_date) || expansion.release_date,
                    }
                }),
            }
        })
        let pelem = document.createElement("p")
        pelem.classList.add("card-id")
        pelem.textContent = `#${data.id}`
        this.image_footer.appendChild(pelem)
        pelem = document.createElement("p")
        pelem.classList.add("card-print")
        if (sets.some(isInPrint)) {
            pelem.textContent = "Currently in print"
        } else {
            pelem.textContent = "Not in print"
        }
        if (window.getComputedStyle(this.card_sets).display === "none") {
            pelem.textContent += " ▶︎"
        } else {
            pelem.textContent += " ▼"
        }
        pelem.addEventListener("click", (ev) => this.toggleFold(ev))
        this.image_footer.appendChild(pelem)
        this.addCardText(text, data.types)
        if (translation) {
            this.card_text.appendChild(document.createElement("hr"))
            this.addCardText(translation, data.types, "translation")
        }
        sets.sort(compareSet)
        this.card_sets.appendChild(document.createElement("hr"))
        const existing_scans = await Promise.all(sets.map((set) => set.scan && urlExists(set.scan)))
        for (const [index, set] of sets.entries()) {
            const name = set.name
            let set_info = document.createElement("div")
            set_info.classList.add("set-info")
            let set_name = document.createElement("p")
            set_name.classList.add("set-name")
            if (existing_scans[index]) {
                set_name.classList.add("selectable")
                set_name.addEventListener("click", async (ev) => this.selectSet(set_info, name, set.scan))
                if (name === state.set || set.code === state.set) {
                    await this.selectSet(set_info, name, set.scan)
                }
                set_name.innerHTML = '<span class="icon">&#xf03e</span> '
            }
            if (isInPrint(set)) {
                set_name.innerHTML += `<strong>${name}</strong>`
            } else {
                set_name.innerHTML += name
            }
            set_info.appendChild(set_name)
            let set_detail = document.createElement("div")
            set_detail.classList.add("set-detail")
            set_info.appendChild(set_detail)
            for (const card_print of set.prints) {
                let set_print = document.createElement("p")
                set_print.classList.add("set-print")
                set_print.textContent = ""
                if (card_print.frequency) {
                    set_print.textContent += card_print.frequency
                }
                if (card_print.type === "Precon") {
                    set_print.textContent += card_print.bundle_name
                }
                if (card_print.copies) {
                    set_print.textContent += ` (${card_print.copies})`
                }
                if (card_print.release_date) {
                    set_print.textContent += ` ${card_print.release_date.replace(/([^-]*)-/g, "$1‑")}`
                }
                set_detail.appendChild(set_print)
            }
            this.card_sets.appendChild(set_info)
        }
        let rulings_map = {}
        if (data.rulings && data.rulings.length > 0) {
            let rulings_list = document.createElement("ul")
            rulings_list.setAttribute("class", "rulings-list")
            this.rulings.appendChild(rulings_list)
            for (const ruling of data.rulings) {
                let ruling_item = document.createElement("li")
                // drop the card ID from {id|Card Name} references
                let ruling_markdown = ruling.text.replace(/\{\d+\|([^}]*)\}/g, "{$1}")
                for (const reference of ruling.references) {
                    ruling_markdown = ruling_markdown.replaceAll(
                        reference.text,
                        `[[${reference.label}]](${reference.url})`
                    )
                }
                ruling_item.dataset.markdown = ruling_markdown
                // format first: the reference links below would otherwise be taken for <Card> references
                let ruling_text = formatText(ruling.text)
                for (const reference of ruling.references) {
                    // use non-breaking spaces and hyphens
                    const non_breaking_ref = reference.label.replace(" ", " ").replace(/([^-]*)-/g, "$1‑")
                    ruling_text = ruling_text.replace(
                        reference.text,
                        `<a target="_blank" href="${reference.url}">[${non_breaking_ref}]</a >`
                    )
                    rulings_map[`[${non_breaking_ref}]`] = reference.url
                }
                ruling_item.innerHTML = ruling_text
                addCardEvents(ruling_item)
                let copy_button = document.createElement("span")
                copy_button.classList.add("icon")
                copy_button.classList.add("selectable")
                copy_button.innerHTML = " &#xf328" // FontAwesome clipboard icon
                ruling_item.appendChild(copy_button)
                rulings_list.appendChild(ruling_item)
                copy_button.addEventListener("transitionend", (e) => {
                    if (e.propertyName == "opacity") {
                        e.target.style.opacity = 1
                    }
                })
                copy_button.addEventListener("click", async (e) => {
                    e.target.style.opacity = 0.3
                    try {
                        await navigator.clipboard.writeText(e.target.parentNode.dataset.markdown)
                    } catch { }
                })
            }
            // custom copy event to include ruling link
            rulings_list.addEventListener("copy", (event) => {
                const selection = document.getSelection()
                const markdown = selection.toString().replace(
                    RegExp(
                        Object.keys(rulings_map)
                            .map((x) => x.replace(/(\[|\])/g, "\\$1"))
                            .join("|"),
                        "g"
                    ),
                    (x) => `${x}(${rulings_map[x]})`
                )
                event.clipboardData.setData("text/plain", markdown)
                event.preventDefault()
            })
        } else {
            let pelem = document.createElement("p")
            pelem.textContent = "No ruling registered."
            this.rulings.appendChild(pelem)
        }
        this.results.style.display = "block"
    }
    async fetchCard(name) {
        const response = await fetch(encodeURI(`https://api.krcg.org/card/${encodeUrlParam(name)}`), {
            method: "GET",
            headers: { Accept: "application/json" },
        })
        if (!response.ok) {
            if (response.status >= 500 && response.status < 600) {
                throw Error("KRCG bootstrapping, please wait...")
            } else if (response.status >= 404 && response.status < 600) {
                throw Error(`"${name}" not found.`)
            } else {
                throw Error(response.statusText)
            }
        }
        return await response.json()
    }
    toggleFold(ev) {
        let text = ev.target.textContent
        if (text.match(/▶︎/gu)) {
            ev.target.textContent = text.replace(/▶︎/gu, "▼")
            this.card_sets.style.display = "block"
        } else {
            ev.target.textContent = text.replace(/▼/gu, "▶︎")
            this.card_sets.style.display = "none"
        }
    }
    addCardText(text, types, cla = undefined) {
        const sections = text.split("\n")
        for (let [index, section] of sections.entries()) {
            let pelem = document.createElement("p")
            if (cla) {
                pelem.classList.add(cla)
            }
            if (types.includes("Vampire") || types.includes("Imbued")) {
                // split before formatting: formatText is not idempotent and card names can contain ":"
                const colon = section.indexOf(":")
                if (colon >= 0) {
                    const sect = section.slice(0, colon)
                    const ability = section.slice(colon + 1)
                    pelem.innerHTML = `<strong>${formatText(sect)}:</strong> ${formatAbility(ability)}`
                } else if (types.includes("Vampire") && index === 0) {
                    pelem.innerHTML = `<strong>${formatText(section)}</strong>`
                } else {
                    pelem.innerHTML = formatAbility(section)
                }
            } else if (
                sections.length > 1 &&
                ((index == 0 && section[0] != "[") ||
                    (section[0] == "[" && section[1].toUpperCase() == section[1] && section[4] == "]"))
            ) {
                pelem.innerHTML = `<strong>${formatText(section)}</strong>`
            } else {
                pelem.innerHTML = formatText(section)
            }
            addCardEvents(pelem)
            this.card_text.appendChild(pelem)
        }
    }
}
function isInPrint(set) {
    if (set.code === "POD") {
        return true
    }
    if (set.code === "Promo" || set.name.match(/promo/i)) {
        return false
    }
    return set.prints.some((detail) => detail.release_date && detail.release_date >= "2017-05-01")
}
async function fetchExpansions() {
    try {
        const response = await fetch("https://static.krcg.org/data/v5/expansions.json")
        if (response.ok) {
            return Object.fromEntries((await response.json()).map((expansion) => [expansion.code, expansion]))
        }
    } catch { }
    // degrade gracefully: set codes are displayed instead of names
    return {}
}
async function urlExists(url) {
    try {
        response = await fetch(url, { method: "HEAD" })
        if (response.ok) {
            return true
        }
    } catch { }
    return false
}
const disc_map = {
    "[1 CONVICTION]": '<span class="krcg-icon">¤</span>',
    "[2 CONVICTION]": '<span class="krcg-icon">¤¤</span>',
    "[3 CONVICTION]": '<span class="krcg-icon">¤¤¤</span>',
    "[4 CONVICTION]": '<span class="krcg-icon">¤¤¤¤</span>',
    "[5 CONVICTION]": '<span class="krcg-icon">¤¤¤¤¤</span>',
    "[ACTION]": '<span class="krcg-icon">0</span>',
    "[POLITICAL ACTION]": '<span class="krcg-icon">2</span>',
    "[REACTION]": '<span class="krcg-icon">7</span>',
    "[ACTION MODIFIER]": '<span class="krcg-icon">1</span>',
    "[COMBAT]": '<span class="krcg-icon">4</span>',
    "[REFLEX]": '<span class="krcg-icon">6</span>',
    "[FLIGHT]": '<span class="krcg-icon">^</span>',
    "[MERGED]": '<span class="krcg-icon">µ </span>',
    "[abo]": '<span class="krcg-icon">w</span>',
    "[ABO]": '<span class="krcg-icon">W</span>',
    "[ani]": '<span class="krcg-icon">i</span>',
    "[ANI]": '<span class="krcg-icon">I</span>',
    "[aus]": '<span class="krcg-icon">a</span>',
    "[AUS]": '<span class="krcg-icon">A</span>',
    "[cel]": '<span class="krcg-icon">c</span>',
    "[CEL]": '<span class="krcg-icon">C</span>',
    "[chi]": '<span class="krcg-icon">k</span>',
    "[CHI]": '<span class="krcg-icon">K</span>',
    "[dai]": '<span class="krcg-icon">y</span>',
    "[DAI]": '<span class="krcg-icon">Y</span>',
    "[dem]": '<span class="krcg-icon">e</span>',
    "[DEM]": '<span class="krcg-icon">E</span>',
    "[dom]": '<span class="krcg-icon">d</span>',
    "[DOM]": '<span class="krcg-icon">D</span>',
    "[for]": '<span class="krcg-icon">f</span>',
    "[FOR]": '<span class="krcg-icon">F</span>',
    "[mal]": '<span class="krcg-icon">â</span>',
    "[MAL]": '<span class="krcg-icon">ã</span>',
    "[mel]": '<span class="krcg-icon">m</span>',
    "[MEL]": '<span class="krcg-icon">M</span>',
    "[myt]": '<span class="krcg-icon">x</span>',
    "[MYT]": '<span class="krcg-icon">X</span>',
    "[nec]": '<span class="krcg-icon">n</span>',
    "[NEC]": '<span class="krcg-icon">N</span>',
    "[obe]": '<span class="krcg-icon">b</span>',
    "[OBE]": '<span class="krcg-icon">B</span>',
    "[obf]": '<span class="krcg-icon">o</span>',
    "[OBF]": '<span class="krcg-icon">O</span>',
    "[obt]": '<span class="krcg-icon">$</span>',
    "[OBT]": '<span class="krcg-icon">£</span>',
    "[pot]": '<span class="krcg-icon">p</span>',
    "[POT]": '<span class="krcg-icon">P</span>',
    "[pre]": '<span class="krcg-icon">r</span>',
    "[PRE]": '<span class="krcg-icon">R</span>',
    "[pro]": '<span class="krcg-icon">j</span>',
    "[PRO]": '<span class="krcg-icon">J</span>',
    "[qui]": '<span class="krcg-icon">q</span>',
    "[QUI]": '<span class="krcg-icon">Q</span>',
    "[san]": '<span class="krcg-icon">g</span>',
    "[SAN]": '<span class="krcg-icon">G</span>',
    "[ser]": '<span class="krcg-icon">s</span>',
    "[SER]": '<span class="krcg-icon">S</span>',
    "[spi]": '<span class="krcg-icon">z</span>',
    "[SPI]": '<span class="krcg-icon">Z</span>',
    "[str]": '<span class="krcg-icon">à</span>',
    "[STR]": '<span class="krcg-icon">á</span>',
    "[tem]": '<span class="krcg-icon">?</span>',
    "[TEM]": '<span class="krcg-icon">!</span>',
    "[thn]": '<span class="krcg-icon">h</span>',
    "[THN]": '<span class="krcg-icon">H</span>',
    "[tha]": '<span class="krcg-icon">t</span>',
    "[THA]": '<span class="krcg-icon">T</span>',
    "[val]": '<span class="krcg-icon">l</span>',
    "[VAL]": '<span class="krcg-icon">L</span>',
    "[vic]": '<span class="krcg-icon">v</span>',
    "[VIC]": '<span class="krcg-icon">V</span>',
    "[vis]": '<span class="krcg-icon">u</span>',
    "[VIS]": '<span class="krcg-icon">U</span>',
}
function formatText(text) {
    // replace card names by span with card image popup (first as disciplines map introduce < in the text)
    // card references are <Card Name> in card texts and {id|Card Name} in rulings
    // replace disciplines text with icons
    return text
        .replace(/<([^<>]*)>|\{(?:\d+\|)?([^}]*)\}/g, (_, x, y) => {
            const name = x ?? y
            return (
                `<span class="krcg-card" data-name="${name.replace("'", "").replace('"', "")}">` +
                `${name.replace(" ", " ")}</span>`
            )
        })
        .replace(
            RegExp(
                Object.keys(disc_map)
                    .map((x) => x.replace(/(\[|\])/g, "\\$1"))
                    .join("|"),
                "g"
            ),
            (x) => disc_map[x]
        )
}
function formatAbility(text) {
    // bold the vampire's bonuses (+1 bleed) and traits (Scarce, Black Hand...)
    return formatText(text)
        .replace(/(?:\.\s\+)([^\.]*)/g, (_, x) => `. <strong>+${x.replace(" ", " ")}</strong>`)
        .replace(
            /(?:\.\s)(Scarce|Black Hand|Red List|Seraph|Infernal|Slave|Sterile)/g,
            (_, x) => `. <strong>${x.replace(" ", " ")}</strong>`
        )
}
function compareSet(a, b) {
    const latest = (set) =>
        Math.max(...set.prints.map((o) => new Date(o.release_date || "1990-01-01")))
    const ret = latest(b) - latest(a)
    if (ret === 0) {
        return a.name.localeCompare(b.name)
    }
    return ret
}
function addCardEvents(pelem) {
    for (let elem of pelem.children) {
        if (elem.classList.contains("krcg-card")) {
            elem.addEventListener("click", clickCard.bind(elem))
            elem.addEventListener("mouseover", overCard.bind(elem))
            elem.addEventListener("mouseout", outCard)
        }
    }
}
async function load() {
    let cardSearch = new CardSearch()
    await cardSearch.state.setup()
}
window.addEventListener("load", load)
