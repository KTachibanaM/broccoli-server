import React from "react"
import ApiClient from "../api/ApiClient";

interface Props {
  apiClient: ApiClient
}

interface State {
  threadCount: number
}

class Debug extends React.Component<Props, State> {
  constructor(props) {
    super(props);
    this.state = {
      threadCount: -1
    }
  }

  componentDidMount() {
    this.props.apiClient.getThreadCount()
      .then(threadCount => {
        this.setState({ threadCount })
      })
  }

  render() {
    return (
      <p style={{fontFamily: "monospace"}}>
        {`thread_count=${this.state.threadCount}`}
      </p>
    )
  }
}

export default Debug
