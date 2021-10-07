function clean_modal() {
    for (elem of document.querySelectorAll("#krcg-click-modal > p")) {
        elem.remove()
    }
}

function get_cardLink (card) {
    var origin = window.location.origin
    var pathname = window.location.pathname
    pathname = pathname.substr(0,4)
    pathname = pathname + "card-search.html?card="
    pathname = origin + pathname
    card = card.replaceAll(" ","+")
    return pathname + card
}

function extends_clickCard () {
    clean_modal()
    var link = document.createElement("a")
    link.href = get_cardLink(getName(this))
    link.target = "_blank"
    link.innerHTML = "See more about it"
    var see_more = document.createElement("p")
    see_more.append(link)
    document.getElementById('krcg-click-image').after(see_more)
}

for (elem of document.querySelectorAll(".krcg-card")) {
    elem.addEventListener("click", extends_clickCard.bind(elem))
}
