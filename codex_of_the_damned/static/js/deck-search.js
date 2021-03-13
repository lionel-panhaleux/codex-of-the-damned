class DeckSearch {
    constructor() {
        this.form = document.getElementById("deck-search-form")
        this.cardList = document.getElementById("deck-search-cards")
        this.clearButton = document.getElementById("clear-search")
        this.result_message = document.getElementById("result-message")
        this.results = document.getElementById("results")
        this.deckList = document.getElementById("decklist")
        this.comments = document.getElementById("comments")
        this.form.addEventListener("submit", async (ev) => await this.addCard(ev))
        this.threshold25 = document.getElementById("threshold25")
        this.completion = new Completion(document.getElementById("card-name"), completeCardName, this.result_message)
        this.state = new UrlState(async (data) => this.display(data), ["cards"])
        this.clearButton.addEventListener("click", () => this.reset())
        this.threshold25.addEventListener("change", (ev) => this.toggleCompetitors(ev))
    }
    async addCard(ev) {
        ev.preventDefault()
        let card = ev.target.elements["card-name"].value
        let cards = new Set(this.state.state.cards || [])
        cards.add(card)
        cards = [...cards]
        this.state.update({ cards: cards })
        ev.target.elements["card-name"].value = ""
        this.displayCard(card)
        this.displayClearButton()
        this.clearDeck()
        await this.displayDeckChoices(this.state.state)
    }
    async toggleCompetitors(ev) {
        if (this.threshold25.checked) {
            this.state.update({ threshold25: true })
        } else {
            this.state.remove("threshold25")
        }
        this.clearDeck()
        await this.displayDeckChoices(this.state.state)
    }
    async removeCard(ev) {
        let cards = new Set(this.state.state.cards || [])
        this.state.reset()
        cards.delete(ev.target.textContent)
        this.cardList.removeChild(ev.target)
        cards = [...cards]
        if (cards.length > 0) {
            this.state.update({ cards: cards })
        }
        this.displayClearButton()
        this.clearDeck()
        await this.displayDeckChoices(this.state.state)
    }
    reset() {
        this.threshold25.checked = false
        this.clearDeck()
        this.clearDeckChoices()
        this.clearCards()
        this.displayClearButton()
        this.state.reset()
    }
    async display(data) {
        if (data.threshold25) {
            this.threshold25.checked = true
        } else {
            this.threshold25.checked = false
        }
        this.displayCards(data || [])
        this.displayClearButton()
        await Promise.all([this.displayDeckChoices(data || []), this.displayDeck(data)])
    }
    displayCard(card) {
        let cardNode = document.createElement("div")
        cardNode.classList.add("deck-search-card")
        cardNode.textContent = card
        cardNode.addEventListener("click", async (e) => await this.removeCard(e))
        this.cardList.append(cardNode)
    }
    clearCards() {
        this.cardList.innerHTML = ""
    }
    displayClearButton() {
        if (this.cardList.children.length > 1) {
            this.clearButton.style.display = "block"
        } else {
            this.clearButton.style.display = "none"
        }
    }
    displayCards(data) {
        this.clearCards()
        if (!data.cards || data.cards.length < 1) {
            return
        }
        for (const card of data.cards) {
            this.displayCard(card)
        }
    }
    clearDeckChoices() {
        this.results.innerHTML = ""
        this.result_message.innerHTML = ""
    }
    async displayDeckChoices(data) {
        this.clearDeckChoices()
        if (!data.cards || data.cards.length < 1) {
            return
        }
        let decks
        try {
            if (data.threshold25) {
                decks = await this.fetchDecks(data.cards, 25)
            } else {
                decks = await this.fetchDecks(data.cards)
            }
        } catch (error) {}
        let message = ""
        if (!decks || decks.length < 1) {
            message = "No result in TWDA."
        } else if (decks.length === 1) {
            message = `1 deck found.`
        } else {
            message = `${decks.length} decks found.`
        }
        this.result_message.innerHTML = `<p>${message}</p>`
        if (!decks) {
            return
        }
        for (const deck of decks) {
            let row = document.createElement("tr")
            row.id = deck.id
            if (data.id == deck.id) {
                row.classList.add("selected")
            }
            let date = document.createElement("td")
            let player = document.createElement("td")
            let name = document.createElement("td")
            date.textContent = deck.date
            player.textContent = wrapText(deck.player, 30)
            name.textContent = wrapText(deck.name, 30)
            row.appendChild(date)
            row.appendChild(player)
            row.appendChild(name)
            row.addEventListener("click", async () => await this.chooseDeck(deck.id))
            this.results.append(row)
        }
    }
    clearDeck() {
        this.deckList.style.display = "none"
        this.comments.innerHTML = ""
        document.getElementById("comments-title").style.display = "none"
        document.getElementById("deck-link").innerHTML = ""
        document.getElementById("crypt-header").innerHTML = ""
        document.getElementById("crypt-list").innerHTML = ""
        document.getElementById("library-header").innerHTML = ""
        document.getElementById("library-list").innerHTML = ""
    }
    async displayDeck(data) {
        this.clearDeck()
        if (!data.id) {
            return
        }
        try {
            displayDeck(await this.fetchDeck(data.id))
        } catch (error) {
            this.result_message.innerHTML = `<p>${error.message}</p>`
        }
        for (let row of this.results.children) {
            row.classList.remove("selected")
            if (row.id === data.id) {
                row.classList.add("selected")
            }
        }
    }
    async fetchDecks(cards, players_count) {
        const response = await fetch(`https://api.krcg.org/twda`, {
            method: "POST",
            body: JSON.stringify({ cards: cards, players_count: players_count || 0 }),
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
            },
        })
        if (!response.ok) {
            if (response.status >= 500 && response.status < 600) {
                throw Error("TWDA bootstrapping, please wait...")
            } else if (response.status >= 404 && response.status < 600) {
                throw Error("No result in TWDA.")
            } else {
                throw Error(response.statusText)
            }
        }
        return await response.json()
    }
    async chooseDeck(id) {
        this.state.update({ id: id })
        await this.displayDeck(this.state.state)
    }
    async fetchDeck(id) {
        const response = await fetch(encodeURI(`https://api.krcg.org/twda/${id}`), {
            method: "GET",
            headers: { Accept: "application/json" },
        })
        if (!response.ok) {
            if (response.status >= 500 && response.status < 600) {
                throw Error("TWDA bootstrapping, please wait...")
            } else if (response.status >= 404 && response.status < 600) {
                throw Error(`Deck #${id} not found.`)
            } else {
                throw Error(response.statusText)
            }
        }
        return await response.json()
    }
}
async function load() {
    let deckSearch = new DeckSearch()
    await deckSearch.state.setup()
}
window.addEventListener("load", load)
