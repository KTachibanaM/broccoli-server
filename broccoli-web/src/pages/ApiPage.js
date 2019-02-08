import React, { Component } from "react"

export default class ApiPage extends Component {
  constructor(props) {
    super(props);

    this.state = {
      "loading": true,
      "qStr": "{}",
      "fieldsStr": "[]"
    }
  }

  componentDidMount() {
    this.props.apiClient.getApiConfig()
      .then(response => {
        const {q, fields} = response.data;
        this.setState({
          "qStr": JSON.stringify(q),
          "fieldsStr": JSON.stringify(fields)
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
    if (this.state.loading) {
      return (<div>Loading...</div>)
    }
    return (
      <div>
        Query:<br/>
        <textarea
          cols="30" rows="5" style={{"resize": "none"}}
          value={this.state.qStr}
          onChange={e => {this.setState({"qStr": e.target.value})}}
        /><br/>
        Fields:<br/>
        <input
          type="text"
          value={this.state.fieldsStr}
          onChange={e => {this.setState({"fieldsStr": e.target.value})}}
        /><br/>
        <button
          onClick={() => {
            this.props.apiClient.setApiConfig(
              JSON.parse(this.state.qStr),
              JSON.parse(this.state.fieldsStr)
            )
              .then(() => {
                this.props.showOkMessage("Set API config")
              })
              .catch(error => {
                this.props.showErrorMessage(error.toString())
              })
          }}
        >Submit</button>
      </div>
    )
  }
}
