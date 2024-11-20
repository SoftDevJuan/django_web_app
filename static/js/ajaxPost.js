const ajaxPost = (url, data, headers = {}) => {
    // Incluye el token CSRF por defecto en los headers
    const defaultHeaders = {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
        ...headers
    };

    return new Promise((resolve, reject) => {
        $.ajax({
            url: url,
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify(data),
            headers: defaultHeaders,
            success: resolve,
            error: reject
        });
    });
};
