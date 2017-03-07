var http = require('http');
var fs = require('fs');
var path = require('path');

const PORT=8080;

var index;
function handleRequest(req, res) {
    try {
        console.log(req.url);
        var filePath = '.' + req.url;
        if (filePath == './')
            filePath = "./index.html";

        var extname = path.extname(filePath);
        var contentType = 'text/html';
        switch (extname) {
            case '.js':
                contentType = 'text/javascript';
                break;
            case '.css':
                contentType = 'text/css';
                break;
            case '.json':
                contentType = 'application/json';
                break;
        }

        fs.readFile(filePath, function(error, content) {
            if (error) {
                if(error.code == 'ENOENT'){
                    fs.readFile('./404.html', function(error, content) {
                        res.writeHead(200, { 'Content-Type': contentType });
                        res.end(content, 'utf-8');
                    });
                }
                else {
                    res.writeHead(500);
                    res.end('Sorry, check with the site admin for error: '+error.code+' ..\n');
                    res.end(); 
                }
            }
            else {
                res.writeHead(200, {'Content-Type': contentType});
                res.end(content);
            }
        });
    } catch(err) {
        console.log(err);
    }
}

var server = http.createServer(handleRequest);

server.listen(PORT, function() {
    console.log("Server listening on: http://localhost:%s", PORT);
});