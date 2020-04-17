import React, { Component } from "react"
import { withRouter } from "react-router-dom";

class Worker extends Component {
  constructor(props) {
    super(props);
    this.workerId = this.props.match.params.workerId;
    this.state = {
      "loading": true,
      "metadataStr": "[]"
    }
  }

  componentDidMount() {
    this.props.apiClient.getWorkerMetadata(this.workerId)
      .then(response => {
        this.setState({
          "metadataStr": JSON.stringify(response.data)
        })
      })
      .catch(error => {
        this.props.showErrorMessage(error.toString())
      })
      .finally(() => {
        this.setState({
          "loading": false
        })
      })
  }

  render() {
    return (
      <div>
        <b>Worker {this.workerId}</b><br/>
        Metadata:<br/>
        <textarea
          cols="30" rows="5" style={{"resize": "none"}}
          value={this.state.metadataStr}
          onChange={e => {this.setState({"metadataStr": e.target.value})}}
        /><br/>
        <button onClick={() => {
          this.props.apiClient.setWorkerMetadata(
            this.workerId,
            JSON.parse(this.state.metadataStr)
          )
            .then(() => {
              this.props.showOkMessage(`Metadata for ${this.workerId} set`)
            })
            .catch(error => {
              this.props.showErrorMessage(error.toString())
            })
        }}>Submit</button>
      </div>
    )
  }
}

export default withRouter(Worker)
