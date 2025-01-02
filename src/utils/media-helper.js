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

class AtriAudio {
  constructor () {
    this.player = new AudioPlayer()
    this.highPerformanceWAVs = [
      '/src/assets/about-setting/high-performance-1.WAV',
      '/src/assets/about-setting/high-performance-2.WAV',
      '/src/assets/about-setting/high-performance-3.WAV',
      '/src/assets/about-setting/high-performance-4.WAV',
      '/src/assets/about-setting/high-performance-5.WAV',
      '/src/assets/about-setting/high-performance-6.WAV',
      '/src/assets/about-setting/high-performance-7.WAV',
      '/src/assets/about-setting/high-performance-8.WAV',
      '/src/assets/about-setting/high-performance-9.WAV',
    ]
  }

  playHighPerformances() {
    this.player.playRandomly(this.highPerformanceWAVs)
  }
}

export const atriAudio = new AtriAudio()
export const audioPlayer = new AudioPlayer()
