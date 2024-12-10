class AudioPlayer {
  constructor() {
    this.audio = null
  }

  play(url) {
    if (this.audio !== null) {
      // 停止当前
      this.audio.pause()
      this.audio.currentTime = 0
    }

    this.audio = new Audio(url)
    this.audio.play() // 播放音频
  }

  playRandomly(urls) {
    const url = this.getRandomElement(urls)
    this.play(url)
  }

  getRandomElement(arr) {
    if (!Array.isArray(arr) || arr.length === 0) return null
    const randomIndex = Math.floor(Math.random() * arr.length)
    return arr[randomIndex]
  }
}

export const audioPlayer = new AudioPlayer()
