const ajaxGet = (url, data) => {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: url,
            method: "GET",
            data: data,
            success: resolve,
            error: reject
        });
    });
};