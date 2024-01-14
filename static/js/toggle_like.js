function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + "=")) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
        }
        }
    }
    return cookieValue;
}

var LikeButtons = document.querySelectorAll(".like-button")
LikeButtons.forEach(function(like_button){
    like_button.addEventListener("click", function(event) {
        // ボタンがクリックされたときに実行されるコード
        var tweetPk = this.getAttribute("data-tweet-pk");

        var data = {pk: tweetPk}
        var likeIconPath = this.querySelector('path');

        // 初期値がセットされていない場合は設定
        if (event.target.dataset.isLiked === undefined) {
            event.target.dataset.isLiked = this.getAttribute("data-is-liked");
        }


        if (event.target.dataset.isLiked === "true"){
            var TweetLikeURL = "/tweets/" + tweetPk + "/unlike/";
            fetch(TweetLikeURL, {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(response => {
                // JSONデータを処理してHTML要素を更新
                var updatedLikesCount = response.likes_count;
                var likesCountElement = this.querySelector('.likes-count');
                likesCountElement.textContent = updatedLikesCount;
                likeIconPath.style.fill = '#FFFFFF';

                event.target.dataset.isLiked = false
                console.log(response, "unlikeが実行された")
            })
            .catch(error => {
                console.error("エラーが発生しました:", error);
            });
        } else {
            var TweetLikeURL = "/tweets/" + tweetPk + "/like/";
            fetch(TweetLikeURL, {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(response => {
                // JSONデータを処理してHTML要素を更新
                var updatedLikesCount = response.likes_count;
                var likesCountElement = this.querySelector('.likes-count');
                likesCountElement.textContent = updatedLikesCount;
                likeIconPath.style.fill = '#BE1931';

                event.target.dataset.isLiked = true;
                console.log(response, "likeが実行された");
                
            })
            .catch(error => {
                console.error("エラーが発生しました:", error);
            });
        };
    });
});
