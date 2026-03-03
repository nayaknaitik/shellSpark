shellspark() {
    local result
    result=$(command shellspark "$@")
    if [ -n "$result" ]; then
        eval "$result"
    fi
}
