import React from "react"

export default function (key) {
  return function (props) {
    const { document } = props;
    return (
      <div>{JSON.stringify(document[key])}</div>
    )
  }
}
