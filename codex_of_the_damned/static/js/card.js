function clearResults() {
    document.getElementById("results").style.display = "none"
    document.getElementById("ruling-submit-tooltip").style.display = "none"
    document.getElementById("rF_submit").disabled = false
    document.getElementById("result-rulings-div").innerHTML = "<h3>Rulings</h3>"
    document.getElementById("result-message").innerHTML = ""
    document.getElementById("result-image").src = ""
    document.getElementById("card-title").textContent = ""
    document.getElementById("card-text").innerHTML = ""
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
            (_, x) =>
                `<span class="card" onclick="dC('${getCardImageName(
                    x
                )}')">${x.replace(" ", " ")}</span>`
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
function displayCard(data, push) {
    clearResults()
    document.getElementById("result-image").src = data["Image"]
    document.getElementById("card-title").textContent = data["Name"]
    document.getElementById("card_info").innerHTML = `#${data["Id"]}<br/>${data[
        "Set"
    ].join(" ")}`
    for (let section of data["Card Text"]
        .replace("{", "")
        .replace("}", "")
        .split("\n")) {
        pelem = document.createElement("p")
        pelem.innerHTML = formatText(section)
        document.getElementById("card-text").appendChild(pelem)
    }
    let rulings_div = document.getElementById("result-rulings-div")
    if (data["Rulings"]) {
        let rulings_list = document.createElement("ul")
        rulings_list.setAttribute("class", "rulings-list")
        rulings_div.appendChild(rulings_list)
        let ruling_links = {}
        for (const rlink of data["Rulings Links"]) {
            ruling_links[rlink["Reference"]] = rlink["URL"]
        }
        for (const ruling of data["Rulings"]) {
            const reference_re = /\[([a-zA-Z0-9]+\s[0-9-]+)\]/g
            let ruling_item = document.createElement("li")
            ruling_item.innerHTML = formatText(ruling.replace(reference_re, ""))
            const references = [...ruling.matchAll(reference_re)]
            for (const reference of references) {
                // use non-breaking spaces and hyphens
                const non_breaking_ref = reference[0]
                    .replace(" ", " ")
                    .replace(/\[([^\]-]*)-([^\]-]*)\]/g, "[$1‑$2]")
                const link = ruling_links[reference[1]]
                ruling_item.innerHTML += ` <a target="_blank" href="${link}">${non_breaking_ref}</a >`
            }
            rulings_list.appendChild(ruling_item)
        }
    } else {
        rulings_div.innerHTML += "<p>No ruling registered.</p>"
    }
    document.getElementById("results").style.display = "block"
    document.getElementById("ruling-submit-tooltip").style.display = "block"
    if (push) {
        window.history.pushState(
            { card: data["Name"] },
            "Card Search",
            encodeURI(`?card=${data["Name"]}`)
        )
    }
    window.document.title = data["Name"]
}
function getCardByName(card_name, push = false) {
    fetch(
        encodeURI(`https://api.krcg.org/card/${card_name.replace("/", "")}`),
        {
            method: "GET",
            headers: { Accept: "application/json" },
        }
    )
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
            document.getElementById(
                "result-message"
            ).innerHTML = `<p>${error.message}</p>`
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
    fetch(encodeURI(`https://api.krcg.org/complete/${text}`), {
        method: "GET",
        headers: { Accept: "application/json" },
    })
        .then(function (response) {
            if (!response.ok) {
                throw Error(response.statusText)
            }
            return response
        })
        .then((response) => response.json())
        .catch(function (error) {
            document.getElementById(
                "result-message"
            ).innerHTML = `<p>${error.message}</p>`
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
    fetch(encodeURI(`https://api.krcg.org/submit-ruling/${card}`), {
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
                    throw Error(
                        "KRCG bootstrapping, please try again in a minute."
                    )
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
            document.getElementById(
                "rf-result"
            ).innerHTML = `<p>${error.message}</p>`
            document.getElementById("rF_submit").disabled = false
            throw error
        })
        .then(function (response) {
            console.log(response)
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
