import axios from "axios"

export default class ApiClient {
  constructor(hostname, port, s3Hostname, s3Port, s3BucketName) {
    this.apiEndpoint = `http://${hostname}:${port}/api`;
    this.s3Endpoint = `http://${s3Hostname}:${s3Port}/${s3BucketName}`;
    this.fromTimestamp = undefined
  }

  nextPage() {
    let url = this.apiEndpoint;
    if (this.fromTimestamp) {
      url = url + `?from=${this.fromTimestamp}`
    }
    return axios.get(url)
      .then(response => {
        const data = response.data;
        const lastItem = data[data.length - 1];
        this.fromTimestamp = lastItem["created_at"] - 1;
        return data.map(item => {
          return {
            ...item,
            "s3_image_link": `${this.s3Endpoint}/${item["s3_image_id"]}`
          }
        })
      })
  }
}
