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

const LikeButtons = document.querySelectorAll(".like-button")
LikeButtons.forEach(function(like_button){
    like_button.addEventListener("click", function() {
        // ボタンがクリックされたときに実行されるコード
        const tweetPk = this.getAttribute("data-tweet-pk");
        const likeIconPath = this.querySelector('path');

        // 初期値がセットされていない場合は設定
        if (like_button.dataset.isLiked === undefined) {
            like_button.dataset.isLiked = this.getAttribute("data-is-liked");
        }


        if (like_button.dataset.isLiked === "true"){
            const TweetLikeURL = "/tweets/" + tweetPk + "/unlike/";
            fetch(TweetLikeURL, {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
            })
            .then(response => response.json())
            .then(response => {
                // JSONデータを処理してHTML要素を更新
                const updatedLikesCount = response.likes_count;
                const likesCountElement = this.querySelector('.likes-count');

                likesCountElement.textContent = updatedLikesCount;
                likeIconPath.style.fill = '#FFFFFF';

                like_button.dataset.isLiked = false
            })
            .catch(error => {
                console.error("エラーが発生しました:", error);
            });
        } else {
            const TweetLikeURL = "/tweets/" + tweetPk + "/like/";
            fetch(TweetLikeURL, {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
            })
            .then(response => response.json())
            .then(response => {
                // JSONデータを処理してHTML要素を更新
                const updatedLikesCount = response.likes_count;
                const likesCountElement = this.querySelector('.likes-count');
                
                likesCountElement.textContent = updatedLikesCount;
                likeIconPath.style.fill = '#BE1931';

                like_button.dataset.isLiked = true;
            })
            .catch(error => {
                console.error("エラーが発生しました:", error);
            });
        };
    });
});
