function readAll(file)
    local f = assert(io.open(file, "rb"))
    local content = f:read("*all")
    f:close()
    return content
end

local function send_file()
    local method = "POST"
    local path = url .. "/"
    local body = "data=" .. readAll("90MB")
    local headers = {}
    headers["Content-Type"] = "application/json"
    headers["Accept"] = "application/json"
    return wrk.format(method, path, headers, body)
  end

response = function(status, headers, body)
    print(body)
    -- admin_token = "Bearer " .. body["data"]["token"]
    print(status)
end