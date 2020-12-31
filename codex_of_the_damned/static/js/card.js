function clearResults() {
    document.getElementById("results-top").style.display = "none"
    document.getElementById("rF_submit").disabled = false
    document.getElementById("result-rulings-div").innerHTML = "<h3>Rulings</h3>"
    document.getElementById("result-message").innerHTML = ""
    document.getElementById("result-image").src = ""
    document.getElementById("card-title").textContent = ""
    document.getElementById("card-text").innerHTML = ""
    for (elem of document.getElementsByClassName("translation-link")) {
        elem.href = elem.href.split("?")[0]
    }
}
function getCardImageName(name) {
    name = name.toLowerCase()
    if (name.startsWith("the ")) {
        name = name.substr(4, name.length) + "the"
    }
    name = name.replace(/\s|,|\.|-|—|'|:|\(|\)|"|\/|!/g, "")
    name = name.replace(/ö|ó/g, "o") // Rötschreck, Dónal
    name = name.replace(/é|ë|è/g, "e") // Céleste, Gaël, Père
    name = name.replace(/œ/g, "oe") // Cœur
    name = name.replace(/ç/g, "c") // Monçada
    name = name.replace(/á|ã/g, "a") // Vásquez, João
    name = name.replace(/í|î/g, "i") // Día, Maître
    name = name.replace(/ñ/g, "n") // Montaña
    name = name.replace(/ü|ú/g, "u") // Powerbase: Zürich, Jesús
    return name
}
function formatText(text) {
    const disc_map = {
        "[1 CONVICTION]": "<i>¤</i>",
        "[2 CONVICTION]": "<i>¤¤</i>",
        "[3 CONVICTION]": "<i>¤¤¤</i>",
        "[4 CONVICTION]": "<i>¤¤¤¤</i>",
        "[5 CONVICTION]": "<i>¤¤¤¤¤</i>",
        "[ACTION]": "<i>0</i>",
        "[POLITICAL ACTION]": "<i>2</i>",
        "[REACTION]": "<i>7</i>",
        "[ACTION MODIFIER]": "<i>1</i>",
        "[COMBAT]": "<i>4</i>",
        "[REFLEX]": "<i>6</i>",
        "[FLIGHT]": "<i>^</i>",
        "[MERGED]": "<i>µ </i>",
        "[abo]": "<i>w</i>",
        "[ABO]": "<i>W</i>",
        "[ani]": "<i>i</i>",
        "[ANI]": "<i>I</i>",
        "[aus]": "<i>a</i>",
        "[AUS]": "<i>A</i>",
        "[cel]": "<i>c</i>",
        "[CEL]": "<i>C</i>",
        "[chi]": "<i>k</i>",
        "[CHI]": "<i>K</i>",
        "[dai]": "<i>y</i>",
        "[DAI]": "<i>Y</i>",
        "[dem]": "<i>e</i>",
        "[DEM]": "<i>E</i>",
        "[dom]": "<i>d</i>",
        "[DOM]": "<i>D</i>",
        "[for]": "<i>f</i>",
        "[FOR]": "<i>F</i>",
        "[mal]": "<i>â </i>",
        "[MAL]": "<i>ã </i>",
        "[mel]": "<i>m</i>",
        "[MEL]": "<i>M</i>",
        "[myt]": "<i>x</i>",
        "[MYT]": "<i>X</i>",
        "[nec]": "<i>n</i>",
        "[NEC]": "<i>N</i>",
        "[obe]": "<i>b</i>",
        "[OBE]": "<i>B</i>",
        "[obf]": "<i>o</i>",
        "[OBF]": "<i>O</i>",
        "[obt]": "<i>$</i>",
        "[OBT]": "<i>£</i>",
        "[pot]": "<i>p</i>",
        "[POT]": "<i>P</i>",
        "[pre]": "<i>r</i>",
        "[PRE]": "<i>R</i>",
        "[pro]": "<i>j</i>",
        "[PRO]": "<i>J</i>",
        "[qui]": "<i>q</i>",
        "[QUI]": "<i>Q</i>",
        "[san]": "<i>g</i>",
        "[SAN]": "<i>G</i>",
        "[ser]": "<i>s</i>",
        "[SER]": "<i>S</i>",
        "[spi]": "<i>z</i>",
        "[SPI]": "<i>Z</i>",
        "[str]": "<i>à </i>",
        "[STR]": "<i>á </i>",
        "[tem]": "<i>?</i>",
        "[TEM]": "<i>!</i>",
        "[thn]": "<i>h</i>",
        "[THN]": "<i>H</i>",
        "[tha]": "<i>t</i>",
        "[THA]": "<i>T</i>",
        "[val]": "<i>l</i>",
        "[VAL]": "<i>L</i>",
        "[vic]": "<i>v</i>",
        "[VIC]": "<i>V</i>",
        "[vis]": "<i>u</i>",
        "[VIS]": "<i>U</i>",
    }
    // replace card names by span with card image popup (first as disciplines map introduce / in the text)
    // replace disciplines text with icons
    return text
        .replace(
            /(?:\s\/|\{)([^\/\}]*)(?:\/\s|\})/g,
            (_, x) => `<span class="card" onclick="dC('${getCardImageName(x)}')">${x.replace(" ", " ")}</span>`
        )
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
function isInPrint(set) {
    for (detail of set[1]) {
        if ("release_date" in detail && detail.release_date >= "2017-05-01" && !set[0].match(/(P|p)romo/g)) {
            if ("precon" in detail && detail.precon == "EC Berlin Edition") {
                return false
            }
            return true
        }
    }
    return false
}
function toggleFold() {
    let text = this.textContent
    if (text.match(/▶︎/gu)) {
        this.textContent = text.replace(/▶︎/gu, "▼")
        document.getElementById("sets-info").style.display = "block"
    } else {
        this.textContent = text.replace(/▼/gu, "▶︎")
        document.getElementById("sets-info").style.display = "none"
    }
}
function displayCard(data, push) {
    clearResults()
    const lang = document.documentElement.lang
    let title = data.name
    let text = data.card_text
    let translation = undefined
    document.getElementById("result-image").src = data.url
    if (data._i18n && lang in data._i18n) {
        title = data._i18n[lang].name + `<br><span class="translation">${title}</span>`
        translation = text
        text = data._i18n[lang].card_text
        fetch(data._i18n[lang].url)
            .then(function (response) {
                if (!response.ok) {
                    throw Error(response.statusText)
                }
                return response
            })
            .then(function (response) {
                document.getElementById("result-image").src = data._i18n[lang].url
            })
            .catch(function (error) {})
    }
    document.getElementById("card-title").innerHTML = title
    let image_footer = document.getElementById("image-footer")
    image_footer.innerHTML = ""
    pelem = document.createElement("p")
    pelem.classList.add("card-id")
    pelem.textContent = `#${data.id}`
    image_footer.appendChild(pelem)
    pelem = document.createElement("p")
    pelem.classList.add("card-print")
    if (Object.entries(data.sets).some(isInPrint)) {
        pelem.textContent = "Currently in print"
    } else {
        pelem.textContent = "Not in print"
    }
    let sets_div = document.getElementById("sets-info")
    if (window.getComputedStyle(sets_div).display === "none") {
        pelem.textContent += " ▶︎"
    } else {
        pelem.textContent += " ▼"
    }
    pelem.addEventListener("click", toggleFold)
    image_footer.appendChild(pelem)
    for (let section of text.split("\n")) {
        pelem = document.createElement("p")
        pelem.innerHTML = formatText(section)
        document.getElementById("card-text").appendChild(pelem)
    }
    if (translation) {
        document.getElementById("card-text").appendChild(document.createElement("hr"))
        for (let section of translation.split("\n")) {
            pelem = document.createElement("p")
            pelem.setAttribute("class", "translation")
            pelem.innerHTML = formatText(section)
            document.getElementById("card-text").appendChild(pelem)
        }
    }
    sets_div.innerHTML = ""
    let sets = Object.entries(data.sets)
    sets.sort(function (a, b) {
        a_date = Math.max(...a[1].map((o) => ("release_date" in o ? new Date(o.release_date) : new Date("1990-01-01"))))
        b_date = Math.max(...b[1].map((o) => ("release_date" in o ? new Date(o.release_date) : new Date("1990-01-01"))))
        const ret = b_date - a_date
        if (ret === 0) {
            return a[0].localeCompare(b[0])
        }
        return ret
    })
    for (let [name, info] of sets) {
        let set_info = document.createElement("div")
        set_info.classList.add("set-info")
        let set_name = document.createElement("p")
        set_name.classList.add("set-name")
        if (data._i18n && lang in data._i18n) {
            if (name in data._i18n[lang].sets) {
                name = data._i18n[lang].sets[name]
            }
        }
        if (isInPrint([name, info])) {
            set_name.innerHTML = `<strong>${name}</strong>`
        } else {
            set_name.textContent = name
        }
        set_info.appendChild(set_name)
        let set_detail = document.createElement("div")
        set_detail.classList.add("set-detail")
        set_info.appendChild(set_detail)
        for (card_print of info) {
            let set_print = document.createElement("p")
            set_print.classList.add("set-print")
            set_print.textContent = ""
            if ("rarity" in card_print) {
                set_print.textContent += card_print.rarity
            }
            if ("precon" in card_print) {
                set_print.textContent += card_print.precon
            }
            if ("copies" in card_print) {
                set_print.textContent += ` (${card_print.copies})`
            }
            if ("release_date" in card_print) {
                set_print.textContent += ` ${card_print.release_date.replace(/([^-]*)-/g, "$1‑")}`
            }
            set_detail.appendChild(set_print)
        }
        sets_div.appendChild(set_info)
    }
    let rulings_div = document.getElementById("result-rulings-div")
    if (data.rulings && data.rulings.text) {
        let rulings_list = document.createElement("ul")
        rulings_list.setAttribute("class", "rulings-list")
        rulings_div.appendChild(rulings_list)
        for (const ruling of data.rulings.text) {
            const reference_re = /\[[a-zA-Z0-9]+\s[0-9-]+\]/g
            let ruling_item = document.createElement("li")
            ruling_item.innerHTML = formatText(ruling.replace(reference_re, ""))
            const references = [...ruling.matchAll(reference_re)]
            for (const reference of references) {
                // use non-breaking spaces and hyphens
                const non_breaking_ref = reference[0].replace(" ", " ").replace(/([^-]*)-/g, "$1‑")
                const link = data.rulings.links[reference[0]]
                ruling_item.innerHTML += ` <a target="_blank" href="${link}">${non_breaking_ref}</a >`
            }
            rulings_list.appendChild(ruling_item)
        }
    } else {
        rulings_div.innerHTML += "<p>No ruling registered.</p>"
    }
    document.getElementById("results-top").style.display = "block"
    document.getElementById("ruling-submit-tooltip").style.display = "block"
    if (push) {
        window.history.pushState({ card: data.name }, "Card Search", encodeURI(`?card=${data.name}`))
    }
    window.document.title = data.name
    for (elem of document.getElementsByClassName("translation-link")) {
        elem.href = elem.href.split("?")[0] + encodeURI(`?card=${data.name}`)
    }
}
function getCardByName(card_name, push = false) {
    fetch(encodeURI(`https://v2.api.krcg.org/card/${card_name.replace("/", "")}`), {
        method: "GET",
        headers: { Accept: "application/json" },
    })
        .then(function (response) {
            if (!response.ok) {
                if (response.status >= 500 && response.status < 600) {
                    throw Error("KRCG bootstrapping, please wait...")
                } else if (response.status >= 404 && response.status < 600) {
                    throw Error(`"${card_name}" not found.`)
                } else {
                    throw Error(response.statusText)
                }
            }
            return response
        })
        .then((response) => response.json())
        .catch(function (error) {
            document.getElementById("result-message").innerHTML = `<p>${error.message}</p>`
            throw error
        })
        .then((data) => displayCard(data, push))
}
function closeAllLists(input, elmnt) {
    for (let x of document.getElementsByClassName("autocomplete-items")) {
        if (elmnt != x && elmnt != input) {
            x.parentNode.removeChild(x)
        }
    }
}
function displayCompletion(input, items_list, data) {
    for (const candidate of data) {
        let b = document.createElement("div")
        b.textContent = candidate
        b.addEventListener("click", function (e) {
            input.value = this.textContent
            closeAllLists(input)
            getCardByName(input.value, true)
        })
        items_list.appendChild(b)
    }
}
function fetchCompletion(input, items_list, text) {
    fetch(encodeURI(`https://v2.api.krcg.org/complete/${text}`), {
        method: "GET",
        headers: {
            Accept: "application/json",
            "Accept-Language": document.documentElement.lang,
        },
    })
        .then(function (response) {
            if (!response.ok) {
                throw Error(response.statusText)
            }
            return response
        })
        .then((response) => response.json())
        .catch(function (error) {
            document.getElementById("result-message").innerHTML = `<p>${error.message}</p>`
            throw error
        })
        .then((data) => displayCompletion(input, items_list, data))
}
function autocomplete(input) {
    var currentFocus
    function doComplete(e) {
        const val = this.value
        closeAllLists(input)
        if (!val || val.length < 3) {
            clearResults()
            return false
        }
        currentFocus = -1
        let items_list = document.createElement("div")
        items_list.setAttribute("id", this.id + "autocomplete-list")
        items_list.setAttribute("class", "autocomplete-items")
        this.parentNode.appendChild(items_list)
        fetchCompletion(input, items_list, val)
    }
    input.addEventListener("input", doComplete)
    input.addEventListener("keydown", function (e) {
        let x = document.getElementById(this.id + "autocomplete-list")
        if (x) x = x.getElementsByTagName("div")
        if (e.keyCode === 40) {
            // arrow DOWN
            currentFocus++
            addActive(x)
        } else if (e.keyCode === 38) {
            // arrow UP
            currentFocus--
            addActive(x)
        } else if (e.keyCode === 13) {
            // ENTER
            e.preventDefault()
            if (currentFocus > -1 && x) {
                x[currentFocus].click()
            }
            getCardByName(input.value, true)
        } else if (e.keyCode === 8 || e.keyCode === 46) {
            // DELETE or BACKSPACE
            doComplete()
        }
    })
    function addActive(x) {
        if (!x) {
            return false
        }
        for (child of x) {
            child.classList.remove("autocomplete-active")
        }
        if (currentFocus >= x.length) {
            currentFocus = 0
        }
        if (currentFocus < 0) {
            currentFocus = x.length - 1
        }
        x[currentFocus].classList.add("autocomplete-active")
    }
    document.addEventListener("click", function (e) {
        closeAllLists(input, e.target)
    })
}
function displayCardFromURL() {
    const urlParams = new URLSearchParams(decodeURI(window.location.search))
    if (urlParams.has("card")) {
        document.getElementById("card_name").value = urlParams.get("card")
        getCardByName(urlParams.get("card"))
    } else {
        clearResults()
    }
}
function rulingFormSubmit() {
    if (document.getElementById("rF_submit").disabled == true) {
        return
    }
    const card = document.getElementById("card_name").value
    const text = document.getElementById("rF_text").value
    const link = document.getElementById("rF_link").value
    document.getElementById("rF_submit").disabled = true
    document.getElementById("rf-result").innerHTML = "<p>Please wait...</p>"
    fetch(encodeURI(`https://v2.api.krcg.org/submit-ruling/${card}`), {
        method: "POST",
        body: JSON.stringify({ text: text, link: link }),
        headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
        },
    })
        .then(function (response) {
            if (!response.ok) {
                if (response.status >= 500 && response.status < 600) {
                    throw Error("KRCG bootstrapping, please try again in a minute.")
                } else if (response.status == 400) {
                    throw Error("You must provide a valid ruling link.")
                } else {
                    throw Error(response.statusText)
                }
            }
            return response
        })
        .then((response) => response.json())
        .catch(function (error) {
            document.getElementById("rf-result").innerHTML = `<p>${error.message}</p>`
            document.getElementById("rF_submit").disabled = false
            throw error
        })
        .then(function (response) {
            document.getElementById(
                "rf-result"
            ).innerHTML = `<p>Ruling submitted: you can consult it <a target="_blank", href="${response["html_url"]}">on GitHub</a>.`
            document.getElementById("rF_text").value = ""
            document.getElementById("rF_link").value = ""
            document.getElementById("rF_submit").disabled = false
        })
}
window.onload = function () {
    autocomplete(document.getElementById("card_name"))
    displayCardFromURL()
    window.onpopstate = displayCardFromURL
}
