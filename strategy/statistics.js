function binom(n, k) {
    console.log(`binom ${n}, ${k}`)
    let res = 1
    for (const i of Array(Math.min(k, n - k)).keys()) {
        res *= (n - i) / (i + 1)
    }
    return res
}

function atLeastOne(stack, copies, draws) {
    console.log(`aLO ${stack}, ${copies}, ${draws}`)
    let res = 0
    const denominator = binom(stack, draws)
    for (const i of Array(Math.min(copies, draws)).keys()) {
        res += (
            binom(copies, i + 1) * binom(stack - copies, draws - i - 1)
        ) / denominator
    }
    return res
}

function howManyNeeded(stack, draws, expectation) {
    console.log(`hMN ${stack}, ${draws}, ${expectation}`)
    for (const copies of Array(stack).keys()) {
        const probability = atLeastOne(stack, copies + 1, draws)
        if (probability >= expectation) {
            return copies + 1
        }
    }
}
