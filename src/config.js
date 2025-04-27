import axios from 'axios'
// const response = await axios.get('/config.json')

let config = null
const configPromise = axios.get('/config.json').then(response => {
  config = response.data
  return config
})

export { config, configPromise }
