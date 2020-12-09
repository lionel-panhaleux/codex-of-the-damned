class MultiCardSearch {
    constructor() {
        this.cardList = new Set()
    }
    add(card) {
        this.cardList.add(card)
        document.getElementById("card_name").value = ""
        this.updateView()
    }
    remove(card) {
        this.cardList.delete(card)
        this.updateView()
    }
    clear() {
        this.cardList.clear()
        this.updateView()
    }
    list() {
        return Array.from(this.cardList)
    }
    updateView() {
        let cardListNode = document.getElementById("multi-card-search")
        while (cardListNode.firstChild) {
            cardListNode.removeChild(cardListNode.firstChild)
        }
        for (let card of this.cardList.values()) {
            let cardNode = document.createElement("span")
            cardNode.setAttribute("class", "multi-card-search-card")
            cardNode.textContent = `${card}`
            cardNode.addEventListener("click", function (e) {
                removeMultiCardSearchCard(card)
            })
            cardListNode.append(cardNode)
        }
        if (this.cardList.size > 1) {
            document.getElementById("clear-search-btn").style.display = "block"
        } else {
            document.getElementById("clear-search-btn").style.display = "none"
        }
        if (this.cardList.size > 0) {
            getDeckWithCards(this.list())
        } else {
            clearSearch()
        }
    }
}

var multiCardSearch = new MultiCardSearch()

function removeMultiCardSearchCard(card) {
    multiCardSearch.remove(card)
}

function getDeckWithCards(cards) {
    fetch(`https://api.krcg.org/deck`, {
        method: "POST",
        body: JSON.stringify({ cards: cards }),
        headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
        },
    })
        .then(function (response) {
            if (!response.ok) {
                if (response.status >= 500 && response.status < 600) {
                    throw Error("TWDA bootstrapping, please wait...")
                } else if (response.status >= 404 && response.status < 600) {
                    throw Error("No example found in TWDA.")
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
        .then((data) => displayDeckChoices(data))
}
function getDeckByID(element, twda_id) {
    fetch(encodeURI(`https://api.krcg.org/deck/${twda_id}`), {
        method: "GET",
        headers: { Accept: "application/json" },
    })
        .then(function (response) {
            if (!response.ok) {
                if (response.status >= 500 && response.status < 600) {
                    throw Error("TWDA bootstrapping, please wait...")
                } else if (response.status >= 404 && response.status < 600) {
                    throw Error(`Deck #${twda_id} not found.`)
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
        .then((data) => displayDeck(data))

    if (element) {
        window.history.pushState(
            { twda_id: twda_id },
            "TWDA",
            `?twda_id=${twda_id}`
        )
        for (let sibling of element.parentElement.children) {
            sibling.classList.remove("selected")
        }
        element.classList.add("selected")
    }
}
function displayDeckChoices(data) {
    removeComments()
    let list = ""
    let message = ""
    if (!data || data.length < 1) {
        message = "No result in TWDA."
    } else if (data.length === 1) {
        message = `1 deck found.`
    } else {
        message = `${data.length} decks found.`
    }
    document.getElementById("result-message").innerHTML = `<p>${message}</p>`
    for (const deck of data) {
        list += `
        <tr class="results">
            <td class="results date" onclick="getDeckByID(this.parentNode, '${
                deck["twda_id"]
            }')">${deck["date"]}</td>
            <td class="results player" onclick="getDeckByID(this.parentNode, '${
                deck["twda_id"]
            }')">${wrapText(deck["player"], 40)}</td>
            <td class="results name" onclick="getDeckByID(this.parentNode, '${
                deck["twda_id"]
            }')">${wrapText(deck["name"], 80)}</td>
        </tr>
        `
    }
    document.getElementById("results").innerHTML = list
}
function displayCompletion(input, items_list, data) {
    for (const candidate of data) {
        let b = document.createElement("DIV")
        b.textContent = candidate
        b.addEventListener("click", function (e) {
            input.value = this.textContent
            closeAllLists(input)
            multiCardSearch.add(input.value)
        })
        items_list.appendChild(b)
    }
}
function fetchCompletion(input, items_list, text) {
    fetch(encodeURI(`https://api.krcg.org/complete/${text}`), {
        method: "GET",
        headers: {
            "Accept": "application/json", 
            "Accept-Language": document.documentElement.lang
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
            document.getElementById("results").textContent = error.message
            throw error
        })
        .then((data) => displayCompletion(input, items_list, data))
}
function clearMultiCardSearch() {
    multiCardSearch.clear()
    clearSearch()
}
function clearSearch() {
    document.getElementById("decklist").style.display = "none"
    document.getElementById("comments-title").style.display = "none"
    document.getElementById("results").innerHTML = ""
    document.getElementById("result-message").innerHTML = ""
    removeComments()
}
function autocomplete(input) {
    var currentFocus
    function doComplete(e) {
        const val = this.value
        closeAllLists(input)
        if (!val || val.length < 3) {
            clearSearch()
            return false
        }
        currentFocus = -1
        let items_list = document.createElement("DIV")
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
function closeAllLists(input, elmnt) {
    for (let x of document.getElementsByClassName("autocomplete-items")) {
        if (elmnt != x && elmnt != input) {
            x.parentNode.removeChild(x)
        }
    }
}
function displayDeckFromURL() {
    const urlParams = new URLSearchParams(window.location.search)
    if (urlParams.has("twda_id")) {
        getDeckByID(null, urlParams.get("twda_id"))
    } else {
        clearMultiCardSearch()
    }
}
window.onload = function () {
    document
        .getElementById("card-modal")
        .addEventListener("keydown", modalKeydown)
    document.getElementById("card-prev").addEventListener("click", prevCard)
    document.getElementById("card-next").addEventListener("click", nextCard)
    autocomplete(document.getElementById("card_name"))
    displayDeckFromURL()
    window.onpopstate = displayDeckFromURL
}
