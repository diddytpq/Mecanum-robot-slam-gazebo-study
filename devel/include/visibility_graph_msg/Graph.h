// Generated by gencpp from file visibility_graph_msg/Graph.msg
// DO NOT EDIT!


#ifndef VISIBILITY_GRAPH_MSG_MESSAGE_GRAPH_H
#define VISIBILITY_GRAPH_MSG_MESSAGE_GRAPH_H


#include <string>
#include <vector>
#include <map>

#include <ros/types.h>
#include <ros/serialization.h>
#include <ros/builtin_message_traits.h>
#include <ros/message_operations.h>

#include <std_msgs/Header.h>
#include <visibility_graph_msg/Node.h>

namespace visibility_graph_msg
{
template <class ContainerAllocator>
struct Graph_
{
  typedef Graph_<ContainerAllocator> Type;

  Graph_()
    : header()
    , robot_id(0)
    , nodes()
    , size(0)  {
    }
  Graph_(const ContainerAllocator& _alloc)
    : header(_alloc)
    , robot_id(0)
    , nodes(_alloc)
    , size(0)  {
  (void)_alloc;
    }



   typedef  ::std_msgs::Header_<ContainerAllocator>  _header_type;
  _header_type header;

   typedef uint16_t _robot_id_type;
  _robot_id_type robot_id;

   typedef std::vector< ::visibility_graph_msg::Node_<ContainerAllocator> , typename ContainerAllocator::template rebind< ::visibility_graph_msg::Node_<ContainerAllocator> >::other >  _nodes_type;
  _nodes_type nodes;

   typedef uint32_t _size_type;
  _size_type size;





  typedef boost::shared_ptr< ::visibility_graph_msg::Graph_<ContainerAllocator> > Ptr;
  typedef boost::shared_ptr< ::visibility_graph_msg::Graph_<ContainerAllocator> const> ConstPtr;

}; // struct Graph_

typedef ::visibility_graph_msg::Graph_<std::allocator<void> > Graph;

typedef boost::shared_ptr< ::visibility_graph_msg::Graph > GraphPtr;
typedef boost::shared_ptr< ::visibility_graph_msg::Graph const> GraphConstPtr;

// constants requiring out of line definition



template<typename ContainerAllocator>
std::ostream& operator<<(std::ostream& s, const ::visibility_graph_msg::Graph_<ContainerAllocator> & v)
{
ros::message_operations::Printer< ::visibility_graph_msg::Graph_<ContainerAllocator> >::stream(s, "", v);
return s;
}


template<typename ContainerAllocator1, typename ContainerAllocator2>
bool operator==(const ::visibility_graph_msg::Graph_<ContainerAllocator1> & lhs, const ::visibility_graph_msg::Graph_<ContainerAllocator2> & rhs)
{
  return lhs.header == rhs.header &&
    lhs.robot_id == rhs.robot_id &&
    lhs.nodes == rhs.nodes &&
    lhs.size == rhs.size;
}

template<typename ContainerAllocator1, typename ContainerAllocator2>
bool operator!=(const ::visibility_graph_msg::Graph_<ContainerAllocator1> & lhs, const ::visibility_graph_msg::Graph_<ContainerAllocator2> & rhs)
{
  return !(lhs == rhs);
}


} // namespace visibility_graph_msg

namespace ros
{
namespace message_traits
{





template <class ContainerAllocator>
struct IsMessage< ::visibility_graph_msg::Graph_<ContainerAllocator> >
  : TrueType
  { };

template <class ContainerAllocator>
struct IsMessage< ::visibility_graph_msg::Graph_<ContainerAllocator> const>
  : TrueType
  { };

template <class ContainerAllocator>
struct IsFixedSize< ::visibility_graph_msg::Graph_<ContainerAllocator> >
  : FalseType
  { };

template <class ContainerAllocator>
struct IsFixedSize< ::visibility_graph_msg::Graph_<ContainerAllocator> const>
  : FalseType
  { };

template <class ContainerAllocator>
struct HasHeader< ::visibility_graph_msg::Graph_<ContainerAllocator> >
  : TrueType
  { };

template <class ContainerAllocator>
struct HasHeader< ::visibility_graph_msg::Graph_<ContainerAllocator> const>
  : TrueType
  { };


template<class ContainerAllocator>
struct MD5Sum< ::visibility_graph_msg::Graph_<ContainerAllocator> >
{
  static const char* value()
  {
    return "b97a406653d1d2556343c32a72248362";
  }

  static const char* value(const ::visibility_graph_msg::Graph_<ContainerAllocator>&) { return value(); }
  static const uint64_t static_value1 = 0xb97a406653d1d255ULL;
  static const uint64_t static_value2 = 0x6343c32a72248362ULL;
};

template<class ContainerAllocator>
struct DataType< ::visibility_graph_msg::Graph_<ContainerAllocator> >
{
  static const char* value()
  {
    return "visibility_graph_msg/Graph";
  }

  static const char* value(const ::visibility_graph_msg::Graph_<ContainerAllocator>&) { return value(); }
};

template<class ContainerAllocator>
struct Definition< ::visibility_graph_msg::Graph_<ContainerAllocator> >
{
  static const char* value()
  {
    return "Header header\n"
"uint16 robot_id\n"
"visibility_graph_msg/Node[] nodes\n"
"uint32 size\n"
"================================================================================\n"
"MSG: std_msgs/Header\n"
"# Standard metadata for higher-level stamped data types.\n"
"# This is generally used to communicate timestamped data \n"
"# in a particular coordinate frame.\n"
"# \n"
"# sequence ID: consecutively increasing ID \n"
"uint32 seq\n"
"#Two-integer timestamp that is expressed as:\n"
"# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')\n"
"# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')\n"
"# time-handling sugar is provided by the client library\n"
"time stamp\n"
"#Frame this data is associated with\n"
"string frame_id\n"
"\n"
"================================================================================\n"
"MSG: visibility_graph_msg/Node\n"
"Header header\n"
"uint32 id\n"
"uint8 FreeType\n"
"geometry_msgs/Point position\n"
"geometry_msgs/Point[] surface_dirs\n"
"bool is_covered\n"
"bool is_frontier\n"
"bool is_navpoint\n"
"bool is_boundary\n"
"uint32[] connect_nodes\n"
"uint32[] poly_connects\n"
"uint32[] contour_connects\n"
"uint32[] trajectory_connects\n"
"================================================================================\n"
"MSG: geometry_msgs/Point\n"
"# This contains the position of a point in free space\n"
"float64 x\n"
"float64 y\n"
"float64 z\n"
;
  }

  static const char* value(const ::visibility_graph_msg::Graph_<ContainerAllocator>&) { return value(); }
};

} // namespace message_traits
} // namespace ros

namespace ros
{
namespace serialization
{

  template<class ContainerAllocator> struct Serializer< ::visibility_graph_msg::Graph_<ContainerAllocator> >
  {
    template<typename Stream, typename T> inline static void allInOne(Stream& stream, T m)
    {
      stream.next(m.header);
      stream.next(m.robot_id);
      stream.next(m.nodes);
      stream.next(m.size);
    }

    ROS_DECLARE_ALLINONE_SERIALIZER
  }; // struct Graph_

} // namespace serialization
} // namespace ros

namespace ros
{
namespace message_operations
{

template<class ContainerAllocator>
struct Printer< ::visibility_graph_msg::Graph_<ContainerAllocator> >
{
  template<typename Stream> static void stream(Stream& s, const std::string& indent, const ::visibility_graph_msg::Graph_<ContainerAllocator>& v)
  {
    s << indent << "header: ";
    s << std::endl;
    Printer< ::std_msgs::Header_<ContainerAllocator> >::stream(s, indent + "  ", v.header);
    s << indent << "robot_id: ";
    Printer<uint16_t>::stream(s, indent + "  ", v.robot_id);
    s << indent << "nodes[]" << std::endl;
    for (size_t i = 0; i < v.nodes.size(); ++i)
    {
      s << indent << "  nodes[" << i << "]: ";
      s << std::endl;
      s << indent;
      Printer< ::visibility_graph_msg::Node_<ContainerAllocator> >::stream(s, indent + "    ", v.nodes[i]);
    }
    s << indent << "size: ";
    Printer<uint32_t>::stream(s, indent + "  ", v.size);
  }
};

} // namespace message_operations
} // namespace ros

#endif // VISIBILITY_GRAPH_MSG_MESSAGE_GRAPH_H