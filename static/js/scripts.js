/*!
    * Start Bootstrap - SB Admin v7.0.7 (https://startbootstrap.com/template/sb-admin)
    * Copyright 2013-2023 Start Bootstrap
    * Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-sb-admin/blob/master/LICENSE)
    */
    // 
// Scripts
// 

window.addEventListener('DOMContentLoaded', event => {

    // Toggle the side navigation
    const sidebarToggle = document.body.querySelector('#sidebarToggle');
    if (sidebarToggle) {
        // Uncomment Below to persist sidebar toggle between refreshes
        // if (localStorage.getItem('sb|sidebar-toggle') === 'true') {
        //     document.body.classList.toggle('sb-sidenav-toggled');
        // }
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
        });
    }

});

function startTutorial() {
    introJs().start();
}


// YouTube APIを使用してデータを取得
function fetchYouTubeVideos() {
    const apiKey = 'AIzaSyBzhjIJonY_CUu2WpptrlbYYsAOF0_dyE8';
    const channelId = 'UCpbAXFvLXA7a4vItLq6h0GQ';
    const url = `https://www.googleapis.com/youtube/v3/search?key=${apiKey}&channelId=${channelId}&part=snippet,id&order=date&maxResults=20`;

    fetch(url)
        .then(response => response.json())
        .then(data => displayYouTubeVideos(data.items));
}

function displayYouTubeVideos(videos) {
    const container = document.getElementById('youtube-container');
    videos.slice(0, 5).forEach(video => {
        const videoElement = document.createElement('div');
        videoElement.className = 'video-card';
        videoElement.innerHTML = `
            <img src="${video.snippet.thumbnails.medium.url}" alt="${video.snippet.description}" class="video-thumbnail">
            <h3 class="title-small">${video.snippet.title}</h3>
            <a href="https://www.youtube.com/watch?v=${video.id.videoId}" target="_blank"class=" read-more-link">ビデオを見る</a>
        `;
        container.appendChild(videoElement);
    });
}

function fetchBlogPosts() {
    const blogApiUrl = 'https://ebay-marketing-tool.com/wp-json/wp/v2/posts';
    fetch(blogApiUrl)
        .then(response => response.json())
        .then(posts => displayBlogPosts(posts));
}

function displayBlogPosts(posts) {
    const container = document.getElementById('blog-container');
    posts.slice(0, 5).forEach(post => {
        const postElement = document.createElement('div');
        postElement.className = 'post-card';

        // サムネイルのURLを取得
        const thumbnailUrl = post._embedded && post._embedded['wp:featuredmedia']
            ? post._embedded['wp:featuredmedia'][0].source_url
            : 'https://ewmqoegsx4q.exactdn.com/wp-content/uploads/2023/08/EXPO3.png?strip=all&lossy=1&ssl=1'; // デフォルトのサムネイルURL

        postElement.innerHTML = `
            <img src="${thumbnailUrl}" alt="${post.title.rendered}" class="post-thumbnail">
            <h3 class="title-small">${post.title.rendered}</h3>
            <a href="${post.link}" target="_blank" class="read-more-link">記事を読む</a>
        `;
        container.appendChild(postElement);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    fetchBlogPosts();
    fetchYouTubeVideos(); // この行を追加
});
